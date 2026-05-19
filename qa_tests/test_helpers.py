import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "qa-test-secret"

from app import Client, User, create_app, db, seed_reference_data


def make_test_app():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        user = User(name="Administrador", username="admin", is_admin=True)
        user.set_password("admin123")
        db.session.add(user)
        seed_reference_data()
        if not Client.query.first():
            db.session.add(Client(name="Cliente Teste", phone="0000-0000"))
        db.session.commit()
    return app


def login(client):
    return client.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=True,
    )
