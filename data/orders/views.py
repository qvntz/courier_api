from data.schema import OrderSchema, CompleteOrder
from flask import Blueprint, jsonify, request
from data import session
from data.models import Order, Courier
from data.tools import generate_RFC_3339, delta_second_RFC_3339, time_chek, set_salary
from data.response_errors import *

orders = Blueprint('orders', __name__)


@orders.route('/orders', methods=['POST'])
def load_orders():
    res = request.json
    invalid = []
    valid = []
    orders_to_append = []

    for order_ in res['data']:
        try:
            if session.query(Order).filter(Order.order_id == order_['order_id']).all():
                invalid.append({"id": order_["order_id"]})
            else:
                o = OrderSchema.parse_obj(order_)
                order = Order(
                    order_id=order_['order_id'],
                    weight=order_['weight'],
                    region=order_['region'],
                    delivery_hours=order_['delivery_hours'])

                valid.append({"id": o.order_id})
                orders_to_append.append(order)

        except Exception as e:
            invalid.append({"id": order_['order_id']})
            continue

    if invalid:
        return response_400({"orders": invalid})

    else:
        session.add_all(orders_to_append)
        session.commit()
        return response_201({"orders": valid})


@orders.route('/orders/assign', methods=['POST'])
def distribution_orders():
    res = request.json

    if len(res.keys()) != 1:
        return response_400_without_info()

    try:
        courier_id = res['courier_id']
        courier = session.query(Courier).get(courier_id)

        if courier.assign_time:
            outstanding_orders = session.query(Order).filter(Order.id_courier == courier_id). \
                filter(Order.second == 0).all()

            response = {"orders": [],
                        "assign_time": courier.assign_time}

            for order_id_ in outstanding_orders.order_id:
                response['orders'].append({"id": order_id_})

            return response_200(response)
        else:

            res = session.query(Order).filter(Order.id_courier == -349,
                                              Order.region.in_(courier.regions),
                                              Order.weight <= courier.weight).all()
            free_weight = courier.weight

            orders_ = []

            for order in res:
                current_weight = free_weight - order.weight
                if current_weight >= 0 and time_chek(courier.working_hours, order.delivery_hours):
                    free_weight = current_weight
                    orders_.append({"id": order.order_id})
                    order.id_courier = courier_id
                    session.query(Order).filter(Order.order_id == order.order_id). \
                        update({
                            'id_courier': courier_id
                        })

            if orders_:
                current_time = generate_RFC_3339()
                response = {
                    "orders": orders_,
                    "assign_time": current_time
                }

                session.query(Courier).filter(Courier.courier_id == courier_id). \
                    update({"assign_time": current_time})
                session.commit()
                return response_200(response)

            else:
                return response_200({"orders": []})

    except Exception as e:
        return response_400_without_info()


@orders.route('/orders/complete', methods=['POST'])
def complete_order():
    res = request.json

    try:
        res = CompleteOrder.parse_obj(res)
        courier_ = session.query(Courier).get(res.courier_id)
        order_ = session.query(Order).filter(Order.order_id == res.order_id). \
            filter(Order.id_courier == res.courier_id). \
            filter(Order.second == 0).first()

        if not order_:
            return response_400_without_info()

        if courier_.current_time:
            order_.second = delta_second_RFC_3339(courier_.current_time,
                                                  res.complete_time)
        else:
            order_.second = delta_second_RFC_3339(courier_.assign_time,
                                                  res.complete_time)

        check_service = session.query(Order).filter(Order.id_courier == res.courier_id). \
            filter(Order.second == 0).all()

        if len(check_service) == 1:
            courier_.current_time = ''
            courier_.assign_time = ''
            courier_.salary += set_salary(courier_.courier_type)
            session.query(Courier).filter(Courier.courier_id == res.courier_id). \
                update({
                    'current_time': courier_.current_time,
                    'assign_time': courier_.assign_time,
                    'salary': courier_.salary
                })
        else:
            courier_.current_time = res.complete_time
            session.query(Courier).filter(Courier.courier_id == res.courier_id). \
                update({
                    'current_time': courier_.current_time,
                })

        session.query(Order).filter(Order.order_id == res.order_id). \
            update({
                'second': order_.second
            })

        session.commit()
        return response_200({"order_id": res.order_id})

    except Exception as e:
        return response_404()