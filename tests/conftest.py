import pytest
import config
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
        db.session.remove()
        db.drop_all()
        db.create_all()
        User.init_db_users() 
        yield flask_app
        db.session.remove()
        db.drop_all()
