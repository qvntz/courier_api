from data.schema import CourierSchema
from flask import Blueprint, jsonify, request
from data import session
from data.models import Courier, Order
from data.tools import determine_type_of_courier, get_rating, assign_to_patch, set_salary
from data.response_errors import *

couriers = Blueprint('couriers', __name__)


@couriers.route('/couriers', methods=['POST'])
def load_courier():
    res = request.json
    invalid = []
    valid = []
    couriers_to_append = []

    for courier_ in res['data']:
        try:
            if session.query(Courier).filter(Courier.courier_id == courier_['courier_id']).all():
                invalid.append({"id": courier_['courier_id']})
            else:
                c = CourierSchema.parse_obj(courier_)
                couriers_to_append.append(determine_type_of_courier(c))
                valid.append({"id": c.courier_id})

        except Exception as e:
            invalid.append({"id": courier_['courier_id']})

    if invalid:
        return response_400({"couriers": invalid})

    else:
        session.add_all(couriers_to_append)
        session.commit()
        return response_201({"couriers": valid})


@couriers.route('/couriers/<int:courier_id>', methods=['PATCH'])
def change_courier_info(courier_id):
    try:
        res = request.json
        courier = session.query(Courier).filter(Courier.courier_id == courier_id).first()
        if courier:
            if courier.current_time:
                courier.salary = set_salary(courier.courier_type)
                session.query(Courier).filter(Courier.courier_id == courier.courier_id).update({
                    'salary': courier.salary
                })
            if 'courier_type' in res and courier.courier_type != res['courier_type']:
                courier.courier_type = res['courier_type']
                if res['courier_type'] == 'foot':
                    courier.weight = 10
                elif res['courier_type'] == 'bike':
                    courier.weight = 15
                elif res['courier_type'] == 'car':
                    courier.weight = 50
            if 'regions' in res and res['regions'] != courier.regions:
                courier.regions = res['regions']

            if 'working_hours' in res and res['working_hours'] != courier.working_hours:
                courier.working_hours = res['working_hours']

            c = CourierSchema.parse_obj({
                'courier_id': courier.courier_id,
                'courier_type': courier.courier_type,
                'regions': courier.regions,
                'working_hours': courier.working_hours
            })

            session.query(Courier).filter(Courier.courier_id == courier_id).update({
                'courier_type': c.courier_type.value,
                'regions': c.regions,
                'working_hours': c.working_hours
            })

            session.commit()
            orders = session.query(Order).filter(Order.id_courier == courier_id,
                                                 Order.second == 0).all()
            if not assign_to_patch(courier, orders):
                raise ValueError('assign to patch error')

            return response_200({
                "courier_id": courier.courier_id,
                "courier_type": courier.courier_type,
                "regions": courier.regions,
                "working_hours": courier.working_hours
            })
        else:
            return response_400_without_info()

    except Exception as e:
        print(e)
        return response_400_without_info()


@couriers.route('/couriers/<int:courier_id>', methods=['GET'])
def get_info(courier_id: int):
    courier_ = session.query(Courier).get(courier_id)

    if not courier_:
        return response_404()

    orders = session.query(Order).filter(Order.id_courier == courier_id,
                                         Order.second != 0).all()
    if not orders:
        return response_200({
            'courier_id': courier_id,
            'courier_type': courier_.courier_type,
            'regions': courier_.regions,
            'working_hours': courier_.working_hours,
            "rating": get_rating(orders),
            'earnings': courier_.salary
        })

    return response_200({
        'courier_id': courier_id,
        'courier_type': courier_.courier_type,
        'regions': courier_.regions,
        'working_hours': courier_.working_hours,
        "rating": get_rating(orders),
        'earnings': courier_.salary
    })
