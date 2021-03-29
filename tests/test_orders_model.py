def test_order_model(order):
    assert order.weight == 4.4


def test_load_orders_failed(client):
    res = client.post('/orders', json={
        "data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": "a",
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 2,
                "weight": "e",
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 3,
                "weight": 0.01,
                "region": 22,
                "delivery_hours": ["13:00-12:00", "16:00-21:30"]
            }]})

    assert res.get_json() == \
           {'validation_error':
               {'orders': [
                   {'id': 1}, {'id': 2}, {'id': 3}]}}


def test_load_orders_ok(client):
    res = client.post('/orders', json={
        "data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 2,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 3,
                "weight": 0.01,
                "region": 22,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"]
            }]})

    assert res.get_json() == {"orders": [{"id": 1}, {"id": 2}, {"id": 3}]}


def test_assign_ok(client):
    res = client.post('/couriers', json={
        "data": [
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            }]})

    res = client.post('/orders', json={
        "data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 2,
                "weight": 4.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 3,
                "weight": 4.23,
                "region": 13,
                "delivery_hours": ["09:00-18:00"]
            }
        ]})

    res = client.post('/orders/assign', json={"courier_id": 1})

    assert res.get_json()['orders'] == [{"id": 1}, {"id": 2}]


def test_assign_failed(client):
    res = client.post('/orders/assign', json={"courier_id": 13})
    assert res.status_code == 400


def test_order_complete_ok(client):
    res = client.post('/couriers', json={
        "data": [
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            }]})

    res = client.post('/orders', json={
        "data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            }]})

    res = client.post('/orders/assign', json={"courier_id": 1})

    res = client.post('/orders/complete', json={"courier_id": 1,
                                                "order_id": 1,
                                                "complete_time": "2121-01-10T10:33:01.42Z"})

    assert res.get_json() == {"order_id": 1}


def test_order_complete_failed(client):
    res = client.post('/orders/complete', json={"courier_id": 1,
                                                "order_id": 1,
                                                "complete_time": "2121-01-10T10:33:01.42Z"})

    assert res.status == "400 BAD REQUEST"