import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret"

from app import Car, CarModel, Client, Employee, Manufacturer, Part, Service, ServiceOrder, User, create_app, db, seed_reference_data


def make_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        user = User(name="Administrador", username="admin", is_admin=True)
        user.set_password("admin123")
        db.session.add(user)
        seed_reference_data()
        client = Client.query.first()
        if not client:
            client = Client(name="Cliente Teste", phone="0000-0000")
            db.session.add(client)
        db.session.commit()
    return app.test_client(), app


def login(client):
    return client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=True)


def test_login_and_dashboard_render():
    client, _ = make_client()
    response = login(client)
    assert response.status_code == 200
    assert b"Painel" in response.data
    assert b"Faturamento" in response.data
    assert b"Servicos por mes" in response.data
    assert b"Carros cadastrados por mes" in response.data
    assert b"Atendimentos a clientes" in response.data

    response = client.get("/graficos")
    assert response.status_code == 200
    assert b"Graficos" in response.data
    assert b"Servicos por mes" in response.data


def test_private_route_redirects_to_login():
    client, _ = make_client()
    response = client.get("/clientes")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_create_client_car_employee_part_service_and_order():
    client, app = make_client()
    login(client)

    response = client.post("/clientes", data={
        "name": "Carlos Souza",
        "phone": "(11) 90000-0000",
        "email": "carlos@email.com",
        "document": "111.222.333-44",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Carlos Souza" in response.data

    response = client.post("/fabricantes", data={"name": "Renault"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Renault" in response.data

    with app.app_context():
        saved_client = Client.query.filter_by(name="Carlos Souza").one()
        manufacturer = Manufacturer.query.filter_by(name="Renault").one()

    response = client.post("/modelos", data={"manufacturer_id": manufacturer.id, "name": "Argo"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Argo" in response.data

    with app.app_context():
        car_model = CarModel.query.filter_by(manufacturer_id=manufacturer.id, name="Argo").one()

    response = client.post("/carros", data={
        "client_id": saved_client.id,
        "manufacturer_id": manufacturer.id,
        "model_id": car_model.id,
        "year": 2022,
        "plate": "ABC1D23",
        "mileage": 32000,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Renault Argo" in response.data

    response = client.post("/funcionarios", data={
        "name": "Ana Lima",
        "role": "Mecanica",
        "phone": "(11) 91111-1111",
        "salary": "4200.00",
        "hourly_cost": "60.00",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Ana Lima" in response.data
    assert b"4.200,00" in response.data

    with app.app_context():
        employee = Employee.query.filter_by(name="Ana Lima").one()

    response = client.post(f"/funcionarios/{employee.id}/editar", data={
        "name": "Ana Lima",
        "role": "Chefe de oficina",
        "phone": "(11) 92222-2222",
        "salary": "5000.00",
        "hourly_cost": "70.00",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Chefe de oficina" in response.data
    assert b"5.000,00" in response.data

    response = client.post("/pecas", data={
        "name": "Correia dentada",
        "sku": "COR-001",
        "stock": 5,
        "cost": "90.00",
        "price": "160.00",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Correia dentada" in response.data

    response = client.post("/servicos", data={
        "name": "Troca de correia",
        "description": "Substituicao preventiva",
        "base_price": "350.00",
        "estimated_hours": "2.00",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Troca de correia" in response.data

    with app.app_context():
        car = Car.query.filter_by(client_id=saved_client.id).one()
        employee = Employee.query.filter_by(name="Ana Lima").one()
        part = Part.query.filter_by(sku="COR-001").one()
        service = Service.query.filter_by(name="Troca de correia").one()

    response = client.post("/ordens", data={
        "client_id": saved_client.id,
        "car_id": car.id,
        "service_id": service.id,
        "employee_id": employee.id,
        "status": "Concluida",
        "hours_spent": "2.50",
        "charged_value": "520.00",
        "part_ids": [part.id],
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Troca de correia" in response.data
    assert b"Concluida" in response.data

    with app.app_context():
        order = ServiceOrder.query.filter_by(employee_id=employee.id).one()

    response = client.post(f"/ordens/{order.id}/editar", data={
        "client_id": saved_client.id,
        "car_id": car.id,
        "service_id": service.id,
        "employee_id": employee.id,
        "status": "Em andamento",
        "hours_spent": "3.00",
        "charged_value": "650.00",
        "part_ids": [part.id],
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Em andamento" in response.data
    assert b"650,00" in response.data

    response = client.get("/")
    assert response.status_code == 200
    assert b"Media por servico" in response.data
    assert b"Servicos por funcionario" in response.data
    assert b"Atendimento a clientes" in response.data
