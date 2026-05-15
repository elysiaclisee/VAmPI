import pytest
from app import app as flask_app
from config import db
from models.user_model import User

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with flask_app.app_context():
        db.create_all()
        User.init_db_users()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_token(client):
    # Lấy token của admin để test các hàm yêu cầu xác thực
    payload = {"username": "admin", "password": "pass1"}
    response = client.post('/users/v1/login', json=payload)
    return response.get_json()['auth_token']