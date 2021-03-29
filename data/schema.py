from pydantic import BaseModel, validator, conint, confloat
from typing import Optional, List
from enum import Enum
from datetime import datetime


class Vehicle(Enum):
    CAR = 'car'
    BIKE = 'bike'
    FOOT = 'foot'


class CourierSchema(BaseModel):
    courier_id: conint(ge=0)
    courier_type: Vehicle
    regions: List[int]
    working_hours: List[str]

    @validator('working_hours')
    def time_valid(cls, v):
        for i in v:
            start_time = i.split('-')[0]
            finish_time = i.split('-')[1]

            if len(start_time + finish_time) != 10:
                raise ValueError('uncorrect time format')

            start_time = datetime.strptime(start_time, '%H:%M')
            finish_time = datetime.strptime(finish_time, '%H:%M')
            if start_time < finish_time:
                continue

            else:
                raise ValueError('uncorrect time format')
        return v


class OrderSchema(BaseModel):
    order_id: conint(ge=0)
    weight: confloat(ge=0.01)
    region: int
    delivery_hours: List[str]
    id_courier: Optional[int]
    second: Optional[int]

    @validator('delivery_hours')
    def time_valid(cls, v):
        for i in v:
            start_time = i.split('-')[0]
            finish_time = i.split('-')[1]

            if len(start_time + finish_time) != 10:
                raise ValueError('uncorrect time format')

            start_time = datetime.strptime(start_time, '%H:%M')
            finish_time = datetime.strptime(finish_time, '%H:%M')
            if start_time < finish_time:
                continue

            else:
                raise ValueError('uncorrect time format')
        return v


class CompleteOrder(BaseModel):
    courier_id: conint(ge=0)
    order_id: conint(ge=0)
    complete_time: str

    @validator('complete_time')
    def time_valid(cls, v):
        datetime.strptime(v[0:22], '%Y-%m-%dT%H:%M:%S.%f')
        return v
