from data.models import Courier, Order
from data.schema import CourierSchema, Vehicle
import json
from datetime import datetime
from data import session as s

def determine_type_of_courier(c: CourierSchema) -> Courier:
    if c.courier_type == Vehicle.FOOT:
        return Courier(courier_id=c.courier_id,
                       courier_type=c.courier_type.value,
                       weight=10,
                       regions=c.regions,
                       working_hours=c.working_hours)

    elif c.courier_type == Vehicle.BIKE:
        return Courier(courier_id=c.courier_id,
                       courier_type=c.courier_type.value,
                       weight=15,
                       regions=c.regions,
                       working_hours=c.working_hours)

    elif c.courier_type == Vehicle.CAR:
        return Courier(courier_id=c.courier_id,
                       courier_type=c.courier_type.value,
                       weight=50,
                       regions=c.regions,
                       working_hours=c.working_hours)


def set_salary(c: Courier.courier_type) -> int:
    if c == 'foot':
        return 1000

    if c == 'bike':
        return 2500

    if c == 'car':
        return 4500


def get_rating(orders: list) -> float:
    frequency = dict()
    for order in orders:
        if order.region not in frequency:
            frequency[order.region] = [order.second]
        else:
            frequency[order.region].append(order.second)

    min_ = 3600
    for i in frequency:
        min_ = min(sum(frequency[i]) / len(frequency[i]), min_)

    return round((3600 - min_) / 3600 * 5, 2)


def generate_RFC_3339() -> str:
    return datetime.utcnow().isoformat("T")[0:22] + "Z"


def delta_second_RFC_3339(time_start: str, time_end: str):
    time_start = datetime.strptime(time_start[0:22], '%Y-%m-%dT%H:%M:%S.%f')
    time_end = datetime.strptime(time_end[0:22], '%Y-%m-%dT%H:%M:%S.%f')
    return int((time_end - time_start).total_seconds())


def get_striptime(time: str) -> datetime:
    return datetime.strptime(time, '%H:%M')


def time_chek(courier_time: list, order_time: list) -> bool:
    for ctime in courier_time:
        start_courier = ctime.split('-')[0]
        finish_courier = ctime.split('-')[1]
        for otime in order_time:
            start_order = otime.split('-')[0]
            finish_order = otime.split('-')[1]
            time = list(map(get_striptime,
                            [start_courier, finish_courier, start_order, finish_order]))

            if not (time[3] <= time[0] or time[1] <= time[2]):
                return True

    return False


def assign_to_patch(courier: Courier, orders: list) -> bool:
    free_weight = courier.weight

    for order in orders:
        if order.region in courier.regions and\
                time_chek(courier.working_hours, order.delivery_hours) and\
                (free_weight - order.weight) >= 0:
            print(order.order_id)
            free_weight -= order.weight
            print(free_weight)
        else:
            try:
                print('ne poshlo', order.order_id)
                order.id_courier = -349
                s.query(Order).filter(Order.order_id == order.order_id). \
                    update({
                        'id_courier': order.id_courier
                    })
                s.commit()
            except Exception as e:
                print(e)
                s.rollback()
                return False

    if free_weight == courier.weight:
        s.query(Courier).filter(Courier.courier_id == courier.courier_id). \
            update({
            'current_time': '',
            'assign_time': ''
        })
        s.commit()

    return True