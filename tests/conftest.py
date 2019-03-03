import pytest

from api import app as app_test


@pytest.yield_fixture
def app():
    app_test.config['DEBUG'] = True
    app_test.config['TESTING'] = True
    app_test.config['SERVER_NAME'] = 'localhost'
    ctx = app_test.app_context()
    ctx.push()
    yield app_test
    ctx.pop()


@pytest.yield_fixture
def client(app):
    yield app.test_client()
