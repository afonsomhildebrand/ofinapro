import unittest
from decimal import Decimal

from test_helpers import make_test_app
from app import (
    Client,
    Employee,
    Payment,
    Part,
    ServiceOrder,
    User,
    UserPermission,
    UserSession,
    db,
    last_month_keys,
    money_value,
    month_label,
    monthly_chart,
)


class UnitAppTests(unittest.TestCase):
    def test_money_value_handles_empty_values(self):
        self.assertEqual(money_value(None), Decimal("0"))
        self.assertEqual(money_value("12.50"), Decimal("12.50"))

    def test_month_helpers_return_expected_shapes(self):
        keys = last_month_keys(6)
        self.assertEqual(len(keys), 6)
        self.assertRegex(keys[-1], r"^\d{4}-\d{2}$")
        self.assertRegex(month_label(keys[-1]), r"^[A-Z][a-z]{2}/\d{2}$")

    def test_monthly_chart_scales_values(self):
        chart = monthly_chart("Teste", ["2026-01", "2026-02", "2026-03"], [0, 5, 10], "#000")
        self.assertEqual(chart["total"], 15)
        self.assertEqual(chart["points"][0]["height"], 0)
        self.assertEqual(chart["points"][2]["height"], 100)

    def test_service_order_costs(self):
        app = make_test_app()
        with app.app_context():
            client = Client.query.first()
            employee = Employee(name="Teste", role="Mecanico", salary=3000, hourly_cost=50)
            part = Part(name="Filtro teste", sku="QA-001", stock=2, cost=40, price=70)
            db.session.add_all([employee, part])
            db.session.commit()
            order = ServiceOrder(
                client_id=client.id,
                car_id=1,
                service_id=1,
                employee_id=employee.id,
                hours_spent=2,
                charged_value=200,
            )
            order.employee = employee
            order.parts = [part]
            db.session.add(order)

            self.assertEqual(order.parts_cost, Decimal("40.00"))
            self.assertEqual(order.labor_cost, Decimal("100.00"))
            self.assertEqual(order.total_cost, Decimal("140.00"))
            self.assertEqual(order.profit, Decimal("60.00"))

    def test_service_order_payment_status(self):
        app = make_test_app()
        with app.app_context():
            order = ServiceOrder(
                client_id=1,
                car_id=1,
                service_id=1,
                employee_id=1,
                hours_spent=1,
                charged_value=300,
            )
            db.session.add(order)
            db.session.flush()
            db.session.add(Payment(order_id=order.id, method="Pix", status="Pago", amount=120, charge_code="PIX-QA"))
            db.session.commit()

            saved_order = db.session.get(ServiceOrder, order.id)
            self.assertEqual(saved_order.paid_amount, Decimal("120.00"))
            self.assertEqual(saved_order.open_balance, Decimal("180.00"))
            self.assertEqual(saved_order.payment_status, "Parcial")

    def test_user_permission_helpers(self):
        app = make_test_app()
        with app.app_context():
            user = User(name="Restrito", username="restrito", is_admin=False)
            user.access_level = "custom"
            user.set_password("123")
            db.session.add(user)
            db.session.flush()
            db.session.add(UserPermission(
                user_id=user.id,
                menu_key="charts",
                can_view=True,
                can_create=False,
                can_edit=False,
                can_delete=False,
            ))
            db.session.commit()

            saved_user = User.query.filter_by(username="restrito").one()
            self.assertTrue(saved_user.can("charts", "can_view"))
            self.assertFalse(saved_user.can("charts", "can_create"))
            self.assertFalse(saved_user.can("clients", "can_view"))

    def test_admin_has_all_permissions_without_rows(self):
        app = make_test_app()
        with app.app_context():
            admin = User.query.filter_by(username="admin").one()
            self.assertTrue(admin.can("users", "can_view"))
            self.assertTrue(admin.can("orders", "can_delete"))
            self.assertTrue(admin.can("billing", "can_create"))

    def test_user_session_duration_seconds(self):
        session = UserSession()
        session.login_at = __import__("datetime").datetime(2026, 1, 1, 10, 0, 0)
        session.last_seen_at = __import__("datetime").datetime(2026, 1, 1, 10, 45, 0)
        self.assertEqual(session.duration_seconds, 2700)


if __name__ == "__main__":
    unittest.main(verbosity=2)
