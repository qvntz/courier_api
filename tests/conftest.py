import pytest
import sys

sys.path.append("..")

from data import app, Base, engine, session as db_session
from data.models import Courier, Order


@pytest.yield_fixture(scope='function')
def testapp():
    _app = app

    Base.metadata.create_all(bind=engine)
    _app.connection = engine.connect()

    yield app

    Base.metadata.drop_all(bind=engine)
    _app.connection.close()


@pytest.fixture(scope='function')
def session(testapp):
    ctx = app.app_context()
    ctx.push()

    yield db_session

    db_session.close_all()
    ctx.pop()


@pytest.fixture(scope='function')
def courier(session):
    courier = Courier(
        courier_id=1,
        courier_type="bike",
        weight=15,
        regions=[1, 2, 3, 4],
        working_hours=["00:00-23:59"]
    )
    session.add(courier)
    session.commit()

    return courier


@pytest.fixture(scope='function')
def order(session):
    order = Order(
        order_id=1,
        weight=4.4,
        region=15,
        delivery_hours=["00:00-23:59"]
    )
    session.add(order)
    session.commit()

    return order


@pytest.fixture
def client(testapp):
    return testapp.test_client()
