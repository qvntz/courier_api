from data.tools import generate_RFC_3339


def test_model(courier):
    assert courier.courier_id == 1


def test_load_failed(client):
    res = client.post('/couriers', json={
        "data": [
            {
                "courier_id": 44,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
            {
                "courier_id": 2,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["09:00-18:00"]
            },
            {
                "courier_id": 3,
                "courier_type": "car",
                "regions": [12, 22, 23, 33],
                "working_hours": []
            },
            {
                "courier_id": 4,
                "courier_type": "scar",
                "regions": [12, 22, 23, 33],
                "working_hours": []
            },
            {
                "courier_id": 5,
                "courier_type": "car",
                "regions": [12, 22, 23, 33],
                "working_hours": ["3413"]
            },
            {
                "courier_id": 6,
                "courier_type": "car",
                "regions": [12, 22, 23, 33],
                "working_hours": ["23:59-04:00"]
            },
            {
                "courier_id": 7,
                "courier_type": "car",
                "regions": ['12, 22, 23, 33'],
                "working_hours": []
            }]
    })

    assert res.get_json() == \
           {'validation_error':
               {'couriers': [
                   {'id': 4}, {'id': 5}, {'id': 6}, {'id': 7}]}}


def test_load_ok(client):
    res = client.post('/couriers', json={
        "data": [
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
            {
                "courier_id": 2,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["09:00-18:00"]
            },
            {
                "courier_id": 3,
                "courier_type": "car",
                "regions": [12, 22, 23, 33],
                "working_hours": []
            }]
    })
    assert res.get_json() == {"couriers": [{"id": 1}, {"id": 2}, {"id": 3}]}


def test_path_ok(client):
    res = client.post('/couriers', json={
        "data": [
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            }]})
    res = client.patch('/couriers/1', json={"regions": [1],
                                            "courier_type": 'foot',
                                            'working_hours': ['00:01-23:59']})

    assert res.get_json() == {"courier_id": 1,
                              "courier_type": "foot",
                              "regions": [1],
                              "working_hours": ["00:01-23:59"]}


def test_path_falied(client):
    res = client.patch('/couriers/17', json={"working_hours": ['']})

    assert res.status == "400 BAD REQUEST"


def test_courier_rating(client):
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
                                                "complete_time": generate_RFC_3339()})

    res = client.get('/couriers/1')
    assert res.get_json()['earnings'] == 1000

