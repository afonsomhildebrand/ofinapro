import unittest

from test_helpers import login, make_test_app
from app import ActivityLog, Car, CarModel, Client, Employee, Manufacturer, Part, Service, ServiceOrder, UserSession, db


class ImplementationAppTests(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()
        self.client = self.app.test_client()

    def test_authentication_flow_and_protected_route(self):
        response = self.client.get("/clientes")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

        response = login(self.client)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Painel", response.data)

    def test_dashboard_and_charts_pages_render(self):
        login(self.client)
        dashboard = self.client.get("/")
        charts = self.client.get("/graficos")
        users = self.client.get("/usuarios")

        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(charts.status_code, 200)
        self.assertEqual(users.status_code, 200)
        self.assertIn(b"Servicos por mes", dashboard.data)
        self.assertIn(b"Carros cadastrados por mes", charts.data)
        self.assertIn(b"Atendimentos a clientes", charts.data)
        self.assertIn(b"Permissoes por menu", users.data)

    def test_user_permission_restricts_menu_access(self):
        login(self.client)
        response = self.client.post("/usuarios", data={
            "name": "Funcionario Servicos",
            "username": "funcionario",
            "password": "senha123",
            "access_level": "employee",
            "is_active_user": "on",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Funcionario Servicos", response.data)

        self.client.get("/logout", follow_redirects=True)
        response = self.client.post("/login", data={"username": "funcionario", "password": "senha123"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        dashboard = self.client.get("/")
        services = self.client.get("/servicos")
        clients = self.client.get("/clientes")
        users = self.client.get("/usuarios")
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(services.status_code, 200)
        self.assertEqual(clients.status_code, 403)
        self.assertEqual(users.status_code, 403)

        create_client = self.client.post("/clientes", data={
            "name": "Bloqueado",
            "phone": "000",
            "email": "",
            "document": "",
        })
        self.assertEqual(create_client.status_code, 403)

        with self.app.app_context():
            blocked = ActivityLog.query.filter_by(action="blocked").first()
            self.assertIsNotNone(blocked)
            self.assertEqual(blocked.menu_key, "clients")

    def test_manager_cannot_access_user_control(self):
        login(self.client)
        response = self.client.post("/usuarios", data={
            "name": "Gerente QA",
            "username": "gerente",
            "password": "senha123",
            "access_level": "manager",
            "is_active_user": "on",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        self.client.get("/logout", follow_redirects=True)
        self.client.post("/login", data={"username": "gerente", "password": "senha123"}, follow_redirects=True)

        self.assertEqual(self.client.get("/clientes").status_code, 200)
        self.assertEqual(self.client.get("/ordens").status_code, 200)
        self.assertEqual(self.client.get("/usuarios").status_code, 403)

    def test_session_and_activity_are_recorded(self):
        login(self.client)
        self.client.get("/graficos")
        self.client.get("/usuarios")
        self.client.get("/logout", follow_redirects=True)

        with self.app.app_context():
            sessions = UserSession.query.all()
            activities = ActivityLog.query.all()
            self.assertGreaterEqual(len(sessions), 1)
            self.assertGreaterEqual(len(activities), 2)
            self.assertIsNotNone(sessions[0].logout_at)

    def test_create_edit_core_workflow(self):
        login(self.client)

        self.client.post("/clientes", data={
            "name": "Cliente QA",
            "phone": "(11) 90000-0000",
            "email": "qa@email.com",
            "document": "123",
        }, follow_redirects=True)
        self.client.post("/fabricantes", data={"name": "QA Motors"}, follow_redirects=True)

        with self.app.app_context():
            client = Client.query.filter_by(name="Cliente QA").one()
            manufacturer = Manufacturer.query.filter_by(name="QA Motors").one()

        self.client.post("/modelos", data={
            "manufacturer_id": manufacturer.id,
            "name": "Modelo QA",
        }, follow_redirects=True)

        with self.app.app_context():
            car_model = CarModel.query.filter_by(manufacturer_id=manufacturer.id, name="Modelo QA").one()

        response = self.client.post("/carros", data={
            "client_id": client.id,
            "manufacturer_id": manufacturer.id,
            "model_id": car_model.id,
            "year": 2026,
            "plate": "QA12345",
            "mileage": 1000,
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Modelo QA", response.data)

        response = self.client.post("/funcionarios", data={
            "name": "Funcionario QA",
            "role": "Tecnico",
            "phone": "(11) 91111-1111",
            "salary": "4500.00",
            "hourly_cost": "75.00",
        }, follow_redirects=True)
        self.assertIn(b"Funcionario QA", response.data)

        self.client.post("/pecas", data={
            "name": "Peca QA",
            "sku": "QA-PEC",
            "stock": 3,
            "cost": "80.00",
            "price": "120.00",
        }, follow_redirects=True)
        self.client.post("/servicos", data={
            "name": "Servico QA",
            "description": "Teste",
            "base_price": "300.00",
            "estimated_hours": "2.00",
        }, follow_redirects=True)

        with self.app.app_context():
            car = Car.query.filter_by(model="Modelo QA").one()
            employee = Employee.query.filter_by(name="Funcionario QA").one()
            part = Part.query.filter_by(sku="QA-PEC").one()
            service = Service.query.filter_by(name="Servico QA").one()

        response = self.client.post("/ordens", data={
            "client_id": client.id,
            "car_id": car.id,
            "service_id": service.id,
            "employee_id": employee.id,
            "status": "Aberta",
            "hours_spent": "2.00",
            "charged_value": "500.00",
            "part_ids": [part.id],
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Servico QA", response.data)

        with self.app.app_context():
            order = ServiceOrder.query.filter_by(employee_id=employee.id).one()

        response = self.client.post(f"/ordens/{order.id}/editar", data={
            "client_id": client.id,
            "car_id": car.id,
            "service_id": service.id,
            "employee_id": employee.id,
            "status": "Concluida",
            "hours_spent": "2.50",
            "charged_value": "650.00",
            "part_ids": [part.id],
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Concluida", response.data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
