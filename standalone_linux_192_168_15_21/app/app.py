from decimal import Decimal
from datetime import datetime
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session as flask_session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, inspect, text
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "Faca login para acessar o sistema."

MENU_ITEMS = [
    {"key": "dashboard", "label": "Painel", "endpoint": "dashboard"},
    {"key": "charts", "label": "Graficos", "endpoint": "charts"},
    {"key": "billing", "label": "Financeiro", "endpoint": "billing"},
    {"key": "clients", "label": "Clientes", "endpoint": "clients", "group": "Cadastros"},
    {"key": "manufacturers", "label": "Fabricantes", "endpoint": "manufacturers", "group": "Cadastros"},
    {"key": "car_models", "label": "Modelos", "endpoint": "car_models", "group": "Cadastros"},
    {"key": "cars", "label": "Carros", "endpoint": "cars", "group": "Cadastros"},
    {"key": "employees", "label": "Funcionarios", "endpoint": "employees", "group": "Cadastros"},
    {"key": "parts", "label": "Pecas", "endpoint": "parts", "group": "Cadastros"},
    {"key": "services", "label": "Servicos", "endpoint": "services", "group": "Cadastros"},
    {"key": "orders", "label": "Ordens", "endpoint": "orders"},
    {"key": "users", "label": "Usuarios do sistema", "endpoint": "users", "group": "Cadastros"},
]

USER_ROLES = [
    {"key": "admin", "label": "Administrador"},
    {"key": "manager", "label": "Gerente"},
    {"key": "employee", "label": "Funcionario"},
    {"key": "custom", "label": "Personalizado"},
]

ROLE_LABELS = {role["key"]: role["label"] for role in USER_ROLES}

ENDPOINT_MENU = {
    "dashboard": "dashboard",
    "charts": "charts",
    "billing": "billing",
    "issue_invoice": "billing",
    "cancel_invoice": "billing",
    "create_payment": "billing",
    "mark_payment_paid": "billing",
    "clients": "clients",
    "edit_client": "clients",
    "manufacturers": "manufacturers",
    "edit_manufacturer": "manufacturers",
    "car_models": "car_models",
    "edit_car_model": "car_models",
    "cars": "cars",
    "edit_car": "cars",
    "employees": "employees",
    "edit_employee": "employees",
    "parts": "parts",
    "edit_part": "parts",
    "services": "services",
    "edit_service": "services",
    "orders": "orders",
    "edit_order": "orders",
    "users": "users",
    "edit_user": "users",
}

DELETE_ENTITY_MENU = {
    "clientes": "clients",
    "fabricantes": "manufacturers",
    "modelos": "car_models",
    "carros": "cars",
    "funcionarios": "employees",
    "pecas": "parts",
    "servicos": "services",
    "ordens": "orders",
    "usuarios": "users",
}


def money_value(value):
    return Decimal(str(value or 0))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    access_level = db.Column(db.String(30), default="custom", nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active_user = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    permissions = db.relationship("UserPermission", back_populates="user", cascade="all, delete-orphan")
    sessions = db.relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    activities = db.relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def role_label(self):
        return ROLE_LABELS.get(self.access_level, "Personalizado")

    @property
    def is_active(self):
        return self.is_active_user

    def permission_for(self, menu_key):
        if self.is_admin:
            return {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True}
        permission = next((item for item in self.permissions if item.menu_key == menu_key), None)
        if not permission:
            return {"can_view": False, "can_create": False, "can_edit": False, "can_delete": False}
        return {
            "can_view": permission.can_view,
            "can_create": permission.can_create,
            "can_edit": permission.can_edit,
            "can_delete": permission.can_delete,
        }

    def can(self, menu_key, action="can_view"):
        return self.permission_for(menu_key).get(action, False)


class UserPermission(db.Model):
    __tablename__ = "user_permissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    menu_key = db.Column(db.String(80), nullable=False)
    can_view = db.Column(db.Boolean, default=False, nullable=False)
    can_create = db.Column(db.Boolean, default=False, nullable=False)
    can_edit = db.Column(db.Boolean, default=False, nullable=False)
    can_delete = db.Column(db.Boolean, default=False, nullable=False)
    user = db.relationship("User", back_populates="permissions")
    __table_args__ = (db.UniqueConstraint("user_id", "menu_key", name="uq_user_menu_permission"),)


class UserSession(db.Model):
    __tablename__ = "user_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    login_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    logout_at = db.Column(db.DateTime)
    user = db.relationship("User", back_populates="sessions")

    @property
    def duration_seconds(self):
        end = self.logout_at or self.last_seen_at or datetime.utcnow()
        return int((end - self.login_at).total_seconds())


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("user_sessions.id"))
    menu_key = db.Column(db.String(80))
    action = db.Column(db.String(40), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    details = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship("User", back_populates="activities")


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(160))
    document = db.Column(db.String(40))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cars = db.relationship("Car", back_populates="client", cascade="all, delete-orphan")
    orders = db.relationship("ServiceOrder", back_populates="client")


class Car(db.Model):
    __tablename__ = "cars"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey("manufacturers.id"))
    model_id = db.Column(db.Integer, db.ForeignKey("car_models.id"))
    manufacturer = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    plate = db.Column(db.String(20), nullable=False, unique=True)
    mileage = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    client = db.relationship("Client", back_populates="cars")
    manufacturer_ref = db.relationship("Manufacturer", back_populates="cars")
    model_ref = db.relationship("CarModel", back_populates="cars")
    orders = db.relationship("ServiceOrder", back_populates="car")


class Manufacturer(db.Model):
    __tablename__ = "manufacturers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    models = db.relationship("CarModel", back_populates="manufacturer", cascade="all, delete-orphan")
    cars = db.relationship("Car", back_populates="manufacturer_ref")


class CarModel(db.Model):
    __tablename__ = "car_models"

    id = db.Column(db.Integer, primary_key=True)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey("manufacturers.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    manufacturer = db.relationship("Manufacturer", back_populates="models")
    cars = db.relationship("Car", back_populates="model_ref")
    __table_args__ = (db.UniqueConstraint("manufacturer_id", "name", name="uq_car_model_manufacturer_name"),)


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(40))
    salary = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    hourly_cost = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    orders = db.relationship("ServiceOrder", back_populates="employee")


class Part(db.Model):
    __tablename__ = "parts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    sku = db.Column(db.String(80), nullable=False, unique=True)
    stock = db.Column(db.Integer, default=0, nullable=False)
    cost = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    price = db.Column(db.Numeric(10, 2), default=0, nullable=False)


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.String(255))
    base_price = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    estimated_hours = db.Column(db.Numeric(8, 2), default=0, nullable=False)
    orders = db.relationship("ServiceOrder", back_populates="service")


order_parts = db.Table(
    "order_parts",
    db.Column("order_id", db.Integer, db.ForeignKey("service_orders.id"), primary_key=True),
    db.Column("part_id", db.Integer, db.ForeignKey("parts.id"), primary_key=True),
)


class ServiceOrder(db.Model):
    __tablename__ = "service_orders"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey("cars.id"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    status = db.Column(db.String(40), default="Aberta", nullable=False)
    hours_spent = db.Column(db.Numeric(8, 2), default=0, nullable=False)
    charged_value = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    client = db.relationship("Client", back_populates="orders")
    car = db.relationship("Car", back_populates="orders")
    service = db.relationship("Service", back_populates="orders")
    employee = db.relationship("Employee", back_populates="orders")
    parts = db.relationship("Part", secondary=order_parts, lazy="joined")
    invoice = db.relationship("Invoice", back_populates="order", uselist=False, cascade="all, delete-orphan")
    payments = db.relationship("Payment", back_populates="order", cascade="all, delete-orphan")

    @property
    def parts_cost(self):
        return sum((money_value(part.cost) for part in self.parts), Decimal("0"))

    @property
    def labor_cost(self):
        return money_value(self.hours_spent) * money_value(self.employee.hourly_cost if self.employee else 0)

    @property
    def total_cost(self):
        return self.parts_cost + self.labor_cost

    @property
    def profit(self):
        return money_value(self.charged_value) - self.total_cost

    @property
    def paid_amount(self):
        return sum((money_value(payment.amount) for payment in self.payments if payment.status == "Pago"), Decimal("0"))

    @property
    def open_balance(self):
        balance = money_value(self.charged_value) - self.paid_amount
        return balance if balance > 0 else Decimal("0")

    @property
    def payment_status(self):
        if self.open_balance <= 0 and money_value(self.charged_value) > 0:
            return "Pago"
        if self.paid_amount > 0:
            return "Parcial"
        return "Pendente"


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("service_orders.id"), nullable=False, unique=True)
    number = db.Column(db.String(40), nullable=False, unique=True)
    status = db.Column(db.String(40), default="Emitida", nullable=False)
    service_description = db.Column(db.String(255), nullable=False)
    customer_name = db.Column(db.String(160), nullable=False)
    customer_document = db.Column(db.String(40))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    notes = db.Column(db.String(255))
    issued_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    canceled_at = db.Column(db.DateTime)
    order = db.relationship("ServiceOrder", back_populates="invoice")


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("service_orders.id"), nullable=False)
    method = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), default="Pendente", nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    due_date = db.Column(db.Date)
    paid_at = db.Column(db.DateTime)
    charge_code = db.Column(db.String(80), nullable=False, unique=True)
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    order = db.relationship("ServiceOrder", back_populates="payments")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def create_app():
    app = Flask(__name__)
    mysql_user = quote_plus(os.getenv("MYSQL_USER", "root"))
    mysql_password = quote_plus(os.getenv("MYSQL_PASSWORD", ""))
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL") or (
        f"mysql+pymysql://{mysql_user}:"
        f"{mysql_password}@"
        f"{os.getenv('MYSQL_HOST', '127.0.0.1')}:"
        f"{os.getenv('MYSQL_PORT', '3306')}/"
        f"{os.getenv('MYSQL_DATABASE', 'oficina_pro')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    register_filters(app)
    register_security(app)
    register_routes(app)
    register_commands(app)
    return app


def register_filters(app):
    @app.template_filter("brl")
    def brl(value):
        number = money_value(value)
        return f"R$ {number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @app.template_filter("hours")
    def hours(value):
        return f"{float(value or 0):.2f}h".replace(".", ",")

    @app.template_filter("duration")
    def duration(seconds):
        total = int(seconds or 0)
        hours_value = total // 3600
        minutes = (total % 3600) // 60
        return f"{hours_value}h {minutes}min"


def action_for_request(endpoint):
    if endpoint == "delete":
        return "can_delete"
    if endpoint in ("cancel_invoice", "mark_payment_paid"):
        return "can_edit"
    if endpoint in ("issue_invoice", "create_payment"):
        return "can_create"
    if endpoint and endpoint.startswith("edit_"):
        return "can_edit"
    if request.method == "POST":
        return "can_create"
    return "can_view"


def current_menu_key():
    if request.endpoint == "delete":
        return DELETE_ENTITY_MENU.get(request.view_args.get("entity"))
    return ENDPOINT_MENU.get(request.endpoint)


def log_activity(action, menu_key=None, details=None):
    if not current_user.is_authenticated:
        return
    session_id = flask_session.get("user_session_id")
    db.session.add(ActivityLog(
        user_id=current_user.id,
        session_id=session_id,
        menu_key=menu_key,
        action=action,
        method=request.method,
        path=request.path[:255],
        details=details,
    ))
    db.session.commit()


def register_security(app):
    @app.context_processor
    def inject_security_helpers():
        visible_menu_items = []
        visible_menu_sections = []
        if current_user.is_authenticated:
            visible_menu_items = [item for item in MENU_ITEMS if current_user.can(item["key"], "can_view")]
            grouped_items = {}
            for item in visible_menu_items:
                group = item.get("group")
                if group:
                    if group not in grouped_items:
                        grouped_items[group] = []
                        visible_menu_sections.append({"type": "group", "label": group, "items": grouped_items[group]})
                    grouped_items[group].append(item)
                else:
                    visible_menu_sections.append({"type": "link", "item": item})
        return {
            "menu_items": MENU_ITEMS,
            "visible_menu_items": visible_menu_items,
            "visible_menu_sections": visible_menu_sections,
            "can_access": lambda key, action="can_view": current_user.is_authenticated and current_user.can(key, action),
        }

    @app.before_request
    def enforce_permissions_and_track_usage():
        if not current_user.is_authenticated or request.endpoint in (None, "static", "login", "logout"):
            return
        session_id = flask_session.get("user_session_id")
        if session_id:
            user_session = db.session.get(UserSession, session_id)
            if user_session and user_session.user_id == current_user.id and not user_session.logout_at:
                user_session.last_seen_at = datetime.utcnow()
                db.session.commit()
        menu_key = current_menu_key()
        if not menu_key:
            return
        action = action_for_request(request.endpoint)
        if not current_user.can(menu_key, action):
            log_activity("blocked", menu_key, f"Sem permissao: {action}")
            abort(403)
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            log_activity(action.replace("can_", ""), menu_key, "Acao executada")


def register_commands(app):
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        ensure_schema_updates()
        if not User.query.filter_by(username="admin").first():
            user = User(name="Administrador", username="admin", is_admin=True)
            user.set_password("admin123")
            db.session.add(user)
        seed_reference_data()
        ensure_admin_permissions()
        db.session.commit()
        print("Banco inicializado. Login: admin | Senha: admin123")


def ensure_schema_updates():
    inspector = inspect(db.engine)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "is_active_user" not in user_columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN is_active_user BOOLEAN NOT NULL DEFAULT 1"))
        db.session.commit()
    if "access_level" not in user_columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN access_level VARCHAR(30) NOT NULL DEFAULT 'custom'"))
        db.session.execute(text("UPDATE users SET access_level = CASE WHEN is_admin = 1 THEN 'admin' ELSE 'custom' END"))
        db.session.commit()
    if "created_at" not in user_columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME NULL"))
        db.session.execute(text("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
        db.session.commit()
    employee_columns = {column["name"] for column in inspector.get_columns("employees")}
    if "salary" not in employee_columns:
        db.session.execute(text("ALTER TABLE employees ADD COLUMN salary NUMERIC(10, 2) NOT NULL DEFAULT 0"))
        db.session.commit()
    for table_name in ("clients", "cars", "service_orders"):
        columns = {column["name"] for column in inspector.get_columns(table_name)}
        if "created_at" not in columns:
            db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN created_at DATETIME NULL"))
            db.session.execute(text(f"UPDATE {table_name} SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
            db.session.commit()
    car_columns = {column["name"] for column in inspector.get_columns("cars")}
    if "manufacturer_id" not in car_columns:
        db.session.execute(text("ALTER TABLE cars ADD COLUMN manufacturer_id INTEGER NULL"))
        db.session.commit()
    if "model_id" not in car_columns:
        db.session.execute(text("ALTER TABLE cars ADD COLUMN model_id INTEGER NULL"))
        db.session.commit()
    sync_existing_car_models()


def sync_existing_car_models():
    for car in Car.query.all():
        manufacturer_name = (car.manufacturer or "").strip()
        model_name = (car.model or "").strip()
        if not manufacturer_name or not model_name:
            continue
        manufacturer = Manufacturer.query.filter(func.lower(Manufacturer.name) == manufacturer_name.lower()).first()
        if not manufacturer:
            manufacturer = Manufacturer(name=manufacturer_name)
            db.session.add(manufacturer)
            db.session.flush()
        car_model = CarModel.query.filter(
            CarModel.manufacturer_id == manufacturer.id,
            func.lower(CarModel.name) == model_name.lower(),
        ).first()
        if not car_model:
            car_model = CarModel(manufacturer_id=manufacturer.id, name=model_name)
            db.session.add(car_model)
            db.session.flush()
        car.manufacturer_id = manufacturer.id
        car.model_id = car_model.id
    db.session.commit()


def seed_reference_data():
    if not Manufacturer.query.first():
        db.session.add_all([
            Manufacturer(name="Chevrolet"),
            Manufacturer(name="Fiat"),
            Manufacturer(name="Ford"),
            Manufacturer(name="Honda"),
            Manufacturer(name="Toyota"),
            Manufacturer(name="Volkswagen"),
        ])
        db.session.flush()
    if not CarModel.query.first():
        model_seed = {
            "Chevrolet": ["Onix", "Prisma", "S10"],
            "Fiat": ["Uno", "Argo", "Toro"],
            "Ford": ["Ka", "Fiesta", "Ranger"],
            "Honda": ["Civic", "Fit", "HR-V"],
            "Toyota": ["Corolla", "Hilux", "Etios"],
            "Volkswagen": ["Gol", "Polo", "T-Cross"],
        }
        for manufacturer_name, model_names in model_seed.items():
            manufacturer = Manufacturer.query.filter_by(name=manufacturer_name).first()
            if not manufacturer:
                continue
            for model_name in model_names:
                db.session.add(CarModel(manufacturer_id=manufacturer.id, name=model_name))
    if not Client.query.first():
        client = Client(name="Mariana Costa", phone="(11) 98888-1111", email="mariana@email.com", document="123.456.789-00")
        db.session.add(client)
    if not Employee.query.first():
        db.session.add(Employee(name="Joao Silva", role="Mecanico", phone="(11) 95555-3333", salary=3500, hourly_cost=48))
    if not Part.query.first():
        db.session.add_all([
            Part(name="Filtro de oleo", sku="FLT-001", stock=12, cost=28, price=48),
            Part(name="Pastilha de freio", sku="FR-220", stock=8, cost=120, price=190),
        ])
    if not Service.query.first():
        db.session.add_all([
            Service(name="Troca de oleo", description="Substituicao de oleo e filtro", base_price=180, estimated_hours=1),
            Service(name="Revisao de freios", description="Inspecao e troca de componentes", base_price=420, estimated_hours=2.5),
        ])


def ensure_admin_permissions():
    for user in User.query.all():
        if user.is_admin:
            user.access_level = "admin"
        defaults = role_permissions(user.access_level)
        for item in MENU_ITEMS:
            permission = UserPermission.query.filter_by(user_id=user.id, menu_key=item["key"]).first()
            if not permission:
                permission = UserPermission(user_id=user.id, menu_key=item["key"])
                db.session.add(permission)
                default = defaults[item["key"]]
                permission.can_view = default["can_view"]
                permission.can_create = default["can_create"]
                permission.can_edit = default["can_edit"]
                permission.can_delete = default["can_delete"]
            if user.is_admin:
                permission.can_view = True
                permission.can_create = True
                permission.can_edit = True
                permission.can_delete = True


def role_permissions(access_level):
    permissions = {}
    for item in MENU_ITEMS:
        key = item["key"]
        permissions[key] = {"can_view": False, "can_create": False, "can_edit": False, "can_delete": False}
        if access_level == "admin":
            permissions[key] = {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True}
        elif access_level == "manager" and key != "users":
            permissions[key] = {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True}
        elif access_level == "employee":
            if key == "dashboard":
                permissions[key]["can_view"] = True
            elif key == "services":
                permissions[key] = {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False}
    return permissions


def apply_user_permissions(user, form):
    UserPermission.query.filter_by(user_id=user.id).delete()
    access_level = form.get("access_level", "custom")
    user.access_level = access_level
    user.is_admin = access_level == "admin"
    defaults = role_permissions(access_level)
    for item in MENU_ITEMS:
        key = item["key"]
        if access_level == "custom":
            can_view = form.get(f"{key}_view") == "on"
            can_create = form.get(f"{key}_create") == "on"
            can_edit = form.get(f"{key}_edit") == "on"
            can_delete = form.get(f"{key}_delete") == "on"
        else:
            permission = defaults[key]
            can_view = permission["can_view"]
            can_create = permission["can_create"]
            can_edit = permission["can_edit"]
            can_delete = permission["can_delete"]
        db.session.add(UserPermission(
            user_id=user.id,
            menu_key=key,
            can_view=can_view,
            can_create=can_create,
            can_edit=can_edit,
            can_delete=can_delete,
        ))


def user_usage_summary(user):
    sessions = UserSession.query.filter_by(user_id=user.id).order_by(UserSession.login_at.desc()).all()
    total_seconds = sum(session.duration_seconds for session in sessions)
    activities_count = ActivityLog.query.filter_by(user_id=user.id).count()
    last_activity = ActivityLog.query.filter_by(user_id=user.id).order_by(ActivityLog.created_at.desc()).first()
    return {
        "sessions": len(sessions),
        "total_seconds": total_seconds,
        "activities_count": activities_count,
        "last_activity": last_activity.created_at if last_activity else None,
    }


def month_key(value):
    current = value or datetime.utcnow()
    return f"{current.year:04d}-{current.month:02d}"


def month_label(key):
    year, month = key.split("-")
    names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    return f"{names[int(month) - 1]}/{year[-2:]}"


def last_month_keys(total=6):
    today = datetime.utcnow()
    year = today.year
    month = today.month
    keys = []
    for offset in range(total - 1, -1, -1):
        current_month = month - offset
        current_year = year
        while current_month <= 0:
            current_month += 12
            current_year -= 1
        keys.append(f"{current_year:04d}-{current_month:02d}")
    return keys


def monthly_chart(title, keys, values, color):
    max_value = max(values) if values else 0
    points = []
    for key, value in zip(keys, values):
        height = round((value / max_value) * 100) if max_value else 0
        points.append({"label": month_label(key), "value": value, "height": height})
    return {"title": title, "points": points, "color": color, "total": sum(values)}


def build_monthly_statistics():
    orders = ServiceOrder.query.all()
    cars = Car.query.all()
    clients = Client.query.all()
    month_keys = last_month_keys(6)
    services_by_month = {key: 0 for key in month_keys}
    cars_by_month = {key: 0 for key in month_keys}
    clients_by_month = {key: 0 for key in month_keys}
    unique_clients_by_month = {key: set() for key in month_keys}

    for order in orders:
        key = month_key(order.created_at)
        if key in services_by_month:
            services_by_month[key] += 1
            clients_by_month[key] += 1
            unique_clients_by_month[key].add(order.client_id)
    for car in cars:
        key = month_key(car.created_at)
        if key in cars_by_month:
            cars_by_month[key] += 1

    unique_clients_total = len(set().union(*unique_clients_by_month.values())) if unique_clients_by_month else 0
    charts = [
        monthly_chart("Servicos por mes", month_keys, [services_by_month[key] for key in month_keys], "#0f766e"),
        monthly_chart("Carros cadastrados por mes", month_keys, [cars_by_month[key] for key in month_keys], "#b45309"),
        monthly_chart("Atendimentos a clientes", month_keys, [clients_by_month[key] for key in month_keys], "#2563eb"),
    ]
    return {
        "charts": charts,
        "total_clients": len(clients),
        "unique_clients_total": unique_clients_total,
    }


def parse_due_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def generate_invoice_number(order):
    return f"NF-{datetime.utcnow().strftime('%Y%m%d')}-{order.id:05d}"


def generate_charge_code(order, method):
    prefix = {
        "Pix": "PIX",
        "Boleto": "BOL",
        "Debito": "DEB",
        "Credito": "CRE",
    }.get(method, "COB")
    return f"{prefix}-{order.id:05d}-{datetime.utcnow().strftime('%H%M%S')}"


def register_routes(app):
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            user = User.query.filter_by(username=request.form["username"].strip()).first()
            if user and user.check_password(request.form["password"]):
                login_user(user)
                user_session = UserSession(user_id=user.id)
                db.session.add(user_session)
                db.session.commit()
                flask_session["user_session_id"] = user_session.id
                log_activity("login", "users", "Login realizado")
                return redirect(url_for("dashboard"))
            flash("Usuario ou senha invalidos.", "error")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        log_activity("logout", "users", "Logout realizado")
        session_id = flask_session.pop("user_session_id", None)
        if session_id:
            user_session = db.session.get(UserSession, session_id)
            if user_session and user_session.user_id == current_user.id and not user_session.logout_at:
                user_session.logout_at = datetime.utcnow()
                user_session.last_seen_at = datetime.utcnow()
                db.session.commit()
        logout_user()
        return redirect(url_for("login"))

    @app.route("/")
    @login_required
    def dashboard():
        orders = ServiceOrder.query.all()
        revenue = sum((money_value(order.charged_value) for order in orders), Decimal("0"))
        total_cost = sum((order.total_cost for order in orders), Decimal("0"))
        parts_cost = sum((order.parts_cost for order in orders), Decimal("0"))
        avg_time = sum((money_value(order.hours_spent) for order in orders), Decimal("0")) / len(orders) if orders else Decimal("0")

        service_averages = []
        for service in Service.query.order_by(Service.name).all():
            service_orders = [order for order in orders if order.service_id == service.id]
            count = len(service_orders)
            service_averages.append({
                "name": service.name,
                "count": count,
                "charged": sum((money_value(order.charged_value) for order in service_orders), Decimal("0")) / count if count else 0,
                "time": sum((money_value(order.hours_spent) for order in service_orders), Decimal("0")) / count if count else 0,
                "profit": sum((order.profit for order in service_orders), Decimal("0")) / count if count else 0,
            })

        employee_stats = []
        for employee in Employee.query.order_by(Employee.name).all():
            employee_orders = [order for order in orders if order.employee_id == employee.id]
            employee_stats.append({
                "name": employee.name,
                "count": len(employee_orders),
                "revenue": sum((money_value(order.charged_value) for order in employee_orders), Decimal("0")),
            })

        monthly_stats = build_monthly_statistics()

        return render_template(
            "dashboard.html",
            revenue=revenue,
            total_cost=total_cost,
            parts_cost=parts_cost,
            profit=revenue - total_cost,
            avg_time=avg_time,
            service_averages=service_averages,
            employee_stats=employee_stats,
            **monthly_stats,
        )

    @app.route("/graficos")
    @login_required
    def charts():
        return render_template("charts.html", **build_monthly_statistics())

    @app.route("/financeiro")
    @login_required
    def billing():
        completed_orders = ServiceOrder.query.filter_by(status="Concluida").order_by(ServiceOrder.id.desc()).all()
        payments = Payment.query.order_by(Payment.created_at.desc()).all()
        invoices = Invoice.query.order_by(Invoice.issued_at.desc()).all()
        total_completed = sum((money_value(order.charged_value) for order in completed_orders), Decimal("0"))
        total_paid = sum((money_value(payment.amount) for payment in payments if payment.status == "Pago"), Decimal("0"))
        total_open = sum((order.open_balance for order in completed_orders), Decimal("0"))
        return render_template(
            "billing.html",
            completed_orders=completed_orders,
            payments=payments,
            invoices=invoices,
            payment_methods=["Pix", "Boleto", "Debito", "Credito"],
            total_completed=total_completed,
            total_paid=total_paid,
            total_open=total_open,
        )

    @app.post("/ordens/<int:order_id>/emitir-nota")
    @login_required
    def issue_invoice(order_id):
        order = db.get_or_404(ServiceOrder, order_id)
        if order.status != "Concluida":
            flash("A nota fiscal so pode ser emitida para servicos concluidos.", "error")
            return redirect(request.referrer or url_for("billing"))
        if order.invoice:
            flash("Esta ordem ja possui nota fiscal.", "error")
            return redirect(request.referrer or url_for("billing"))
        invoice = Invoice(
            order_id=order.id,
            number=generate_invoice_number(order),
            service_description=f"{order.service.name} - {order.car.manufacturer} {order.car.model}",
            customer_name=order.client.name,
            customer_document=order.client.document,
            amount=order.charged_value,
            tax_amount=money_value(order.charged_value) * Decimal("0.05"),
            notes="Controle interno para integracao fiscal externa.",
        )
        db.session.add(invoice)
        db.session.commit()
        flash("Nota fiscal registrada para a ordem concluida.", "success")
        return redirect(request.referrer or url_for("billing"))

    @app.post("/ordens/<int:order_id>/pagamentos")
    @login_required
    def create_payment(order_id):
        order = db.get_or_404(ServiceOrder, order_id)
        if order.status != "Concluida":
            flash("Cobrancas so podem ser geradas para servicos concluidos.", "error")
            return redirect(request.referrer or url_for("billing"))
        method = request.form["method"]
        amount = money_value(request.form.get("amount") or order.open_balance)
        if amount <= 0:
            flash("Informe um valor de cobranca maior que zero.", "error")
            return redirect(request.referrer or url_for("billing"))
        payment = Payment(
            order_id=order.id,
            method=method,
            amount=amount,
            due_date=parse_due_date(request.form.get("due_date")),
            charge_code=generate_charge_code(order, method),
            notes=request.form.get("notes"),
        )
        db.session.add(payment)
        db.session.commit()
        flash("Cobranca gerada.", "success")
        return redirect(request.referrer or url_for("billing"))

    @app.post("/pagamentos/<int:payment_id>/baixar")
    @login_required
    def mark_payment_paid(payment_id):
        payment = db.get_or_404(Payment, payment_id)
        payment.status = "Pago"
        payment.paid_at = datetime.utcnow()
        db.session.commit()
        flash("Pagamento baixado como pago.", "success")
        return redirect(request.referrer or url_for("billing"))

    @app.post("/notas/<int:invoice_id>/cancelar")
    @login_required
    def cancel_invoice(invoice_id):
        invoice = db.get_or_404(Invoice, invoice_id)
        invoice.status = "Cancelada"
        invoice.canceled_at = datetime.utcnow()
        db.session.commit()
        flash("Nota fiscal cancelada no controle interno.", "success")
        return redirect(request.referrer or url_for("billing"))

    register_crud_routes(app)


def register_crud_routes(app):
    @app.route("/usuarios", methods=["GET", "POST"])
    @login_required
    def users():
        if not current_user.is_admin:
            abort(403)
        if request.method == "POST":
            username = request.form["username"].strip()
            access_level = request.form.get("access_level", "custom")
            if User.query.filter_by(username=username).first():
                flash("Usuario ja cadastrado.", "error")
                return redirect(url_for("users"))
            item = User(
                name=request.form["name"].strip(),
                username=username,
                access_level=access_level,
                is_admin=access_level == "admin",
                is_active_user=request.form.get("is_active_user") == "on",
            )
            item.set_password(request.form["password"])
            db.session.add(item)
            db.session.flush()
            apply_user_permissions(item, request.form)
            db.session.commit()
            flash("Usuario salvo.", "success")
            return redirect(url_for("users"))
        items = User.query.order_by(User.name).all()
        summaries = {item.id: user_usage_summary(item) for item in items}
        recent_activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(50).all()
        return render_template("users.html", items=items, summaries=summaries, edit_item=None, menu_items=MENU_ITEMS, user_roles=USER_ROLES, recent_activities=recent_activities)

    @app.route("/usuarios/<int:item_id>/editar", methods=["GET", "POST"])
    @login_required
    def edit_user(item_id):
        if not current_user.is_admin:
            abort(403)
        item = db.get_or_404(User, item_id)
        if request.method == "POST":
            access_level = request.form.get("access_level", "custom")
            duplicate = User.query.filter(User.id != item.id, User.username == request.form["username"].strip()).first()
            if duplicate:
                flash("Usuario ja cadastrado.", "error")
                return redirect(url_for("edit_user", item_id=item.id))
            item.name = request.form["name"].strip()
            item.username = request.form["username"].strip()
            item.access_level = access_level
            item.is_admin = access_level == "admin"
            item.is_active_user = request.form.get("is_active_user") == "on"
            if request.form.get("password"):
                item.set_password(request.form["password"])
            apply_user_permissions(item, request.form)
            db.session.commit()
            flash("Usuario atualizado.", "success")
            return redirect(url_for("users"))
        items = User.query.order_by(User.name).all()
        summaries = {current.id: user_usage_summary(current) for current in items}
        recent_activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(50).all()
        return render_template("users.html", items=items, summaries=summaries, edit_item=item, menu_items=MENU_ITEMS, user_roles=USER_ROLES, recent_activities=recent_activities)

    @app.route("/clientes", methods=["GET", "POST"])
    @login_required
    def clients():
        if request.method == "POST":
            item = Client(
                name=request.form["name"],
                phone=request.form["phone"],
                email=request.form.get("email"),
                document=request.form.get("document"),
            )
            db.session.add(item)
            db.session.commit()
            flash("Cliente salvo.", "success")
            return redirect(url_for("clients"))
        return render_template("clients.html", items=Client.query.order_by(Client.name).all(), edit_item=None)

    @app.route("/clientes/<int:item_id>/editar", methods=["GET", "POST"])
    @login_required
    def edit_client(item_id):
        item = db.get_or_404(Client, item_id)
        if request.method == "POST":
            item.name = request.form["name"]
            item.phone = request.form["phone"]
            item.email = request.form.get("email")
            item.document = request.form.get("document")
            db.session.commit()
            flash("Cliente atualizado.", "success")
            return redirect(url_for("clients"))
        return render_template("clients.html", items=Client.query.order_by(Client.name).all(), edit_item=item)

    @app.route("/carros", methods=["GET", "POST"])
    @login_required
    def cars():
        if request.method == "POST":
            car_model = db.get_or_404(CarModel, request.form["model_id"])
            item = Car(
                client_id=request.form["client_id"],
                manufacturer_id=car_model.manufacturer_id,
                model_id=car_model.id,
                manufacturer=car_model.manufacturer.name,
                model=car_model.name,
                year=request.form["year"],
                plate=request.form["plate"].upper(),
                mileage=request.form.get("mileage") or 0,
            )
            db.session.add(item)
            db.session.commit()
            flash("Carro salvo.", "success")
            return redirect(url_for("cars"))
        return render_template(
            "cars.html",
            items=Car.query.order_by(Car.manufacturer, Car.model).all(),
            clients=Client.query.order_by(Client.name).all(),
            manufacturers=Manufacturer.query.order_by(Manufacturer.name).all(),
            car_models=CarModel.query.join(Manufacturer).order_by(Manufacturer.name, CarModel.name).all(),
            edit_item=None,
        )

    @app.route("/carros/<int:item_id>/editar", methods=["GET", "POST"])
    @login_required
    def edit_car(item_id):
        item = db.get_or_404(Car, item_id)
        if request.method == "POST":
            car_model = db.get_or_404(CarModel, request.form["model_id"])
            item.client_id = request.form["client_id"]
            item.manufacturer_id = car_model.manufacturer_id
            item.model_id = car_model.id
            item.manufacturer = car_model.manufacturer.name
            item.model = car_model.name
            item.year = request.form["year"]
            item.plate = request.form["plate"].upper()
            item.mileage = request.form.get("mileage") or 0
            db.session.commit()
            flash("Carro atualizado.", "success")
            return redirect(url_for("cars"))
        return render_template(
            "cars.html",
            items=Car.query.order_by(Car.manufacturer, Car.model).all(),
            clients=Client.query.order_by(Client.name).all(),
            manufacturers=Manufacturer.query.order_by(Manufacturer.name).all(),
            car_models=CarModel.query.join(Manufacturer).order_by(Manufacturer.name, CarModel.name).all(),
            edit_item=item,
        )

    @app.route("/modelos", methods=["GET", "POST"])
    @login_required
    def car_models():
        if request.method == "POST":
            manufacturer_id = request.form["manufacturer_id"]
            name = request.form["name"].strip()
            duplicate = CarModel.query.filter(
                CarModel.manufacturer_id == manufacturer_id,
                func.lower(CarModel.name) == name.lower(),
            ).first()
            if duplicate:
                flash("Modelo ja cadastrado para este fabricante.", "error")
                return redirect(url_for("car_models"))
            db.session.add(CarModel(manufacturer_id=manufacturer_id, name=name))
            db.session.commit()
            flash("Modelo salvo.", "success")
            return redirect(url_for("car_models"))
        return render_template(
            "car_models.html",
            items=CarModel.query.join(Manufacturer).order_by(Manufacturer.name, CarModel.name).all(),
            manufacturers=Manufacturer.query.order_by(Manufacturer.name).all(),
            edit_item=None,
        )

    @app.route("/modelos/<int:item_id>/editar", methods=["GET", "POST"])
    @login_required
    def edit_car_model(item_id):
        item = db.get_or_404(CarModel, item_id)
        if request.method == "POST":
            manufacturer_id = request.form["manufacturer_id"]
            name = request.form["name"].strip()
            duplicate = CarModel.query.filter(
                CarModel.id != item.id,
                CarModel.manufacturer_id == manufacturer_id,
                func.lower(CarModel.name) == name.lower(),
            ).first()
            if duplicate:
                flash("Modelo ja cadastrado para este fabricante.", "error")
                return redirect(url_for("edit_car_model", item_id=item.id))
            item.manufacturer_id = manufacturer_id
            item.name = name
            manufacturer = db.get_or_404(Manufacturer, manufacturer_id)
            Car.query.filter_by(model_id=item.id).update({
                "manufacturer_id": manufacturer_id,
                "manufacturer": manufacturer.name,
                "model": name,
            })
            db.session.commit()
            flash("Modelo atualizado.", "success")
            return redirect(url_for("car_models"))
        return render_template(
            "car_models.html",
            items=CarModel.query.join(Manufacturer).order_by(Manufacturer.name, CarModel.name).all(),
            manufacturers=Manufacturer.query.order_by(Manufacturer.name).all(),
            edit_item=item,
        )

    @app.route("/fabricantes", methods=["GET", "POST"])
    @login_required
    def manufacturers():
        if request.method == "POST":
            name = request.form["name"].strip()
            if Manufacturer.query.filter(func.lower(Manufacturer.name) == name.lower()).first():
                flash("Fabricante ja cadastrado.", "error")
                return redirect(url_for("manufacturers"))
            db.session.add(Manufacturer(name=name))
            db.session.commit()
            flash("Fabricante salvo.", "success")
            return redirect(url_for("manufacturers"))
        return render_template("manufacturers.html", items=Manufacturer.query.order_by(Manufacturer.name).all(), edit_item=None)

    @app.route("/fabricantes/<int:item_id>/editar", methods=["GET", "POST"])
    @login_required
    def edit_manufacturer(item_id):
        item = db.get_or_404(Manufacturer, item_id)
        if request.method == "POST":
            name = request.form["name"].strip()
            duplicate = Manufacturer.query.filter(Manufacturer.id != item.id, func.lower(Manufacturer.name) == name.lower()).first()
            if duplicate:
                flash("Fabricante ja cadastrado.", "error")
                return redirect(url_for("edit_manufacturer", item_id=item.id))
            old_name = item.name
            item.name = name
            Car.query.filter_by(manufacturer=old_name).update({"manufacturer": name})
            db.session.commit()
            flash("Fabricante atualizado.", "success")
            return redirect(url_for("manufacturers"))
        return render_template("manufacturers.html", items=Manufacturer.query.order_by(Manufacturer.name).all(), edit_item=item)

    @app.route("/funcionarios", methods=["GET", "POST"])
    @login_required
    def employees():
        if request.method == "POST":
            item = Employee(
                name=request.form["name"],
                role=request.form["role"],
                phone=request.form.get("phone"),
                salary=request.form["salary"],
                hourly_cost=request.form["hourly_cost"],
            )
            db.session.add(item)
            db.session.commit()
            flash("Funcionario salvo.", "success")
            return redirect(url_for("employees"))
        return render_template("employees.html", items=Employee.query.order_by(Employee.name).all(), edit_item=None)

    @app.route("/funcionarios/<int:item_id>/editar", methods=["GET", "POST"])
    @login_required
    def edit_employee(item_id):
        item = db.get_or_404(Employee, item_id)
        if request.method == "POST":
            item.name = request.form["name"]
            item.role = request.form["role"]
            item.phone = request.form.get("phone")
            item.salary = request.form["salary"]
            item.hourly_cost = request.form["hourly_cost"]
            db.session.commit()
            flash("Funcionario atualizado.", "success")
            return redirect(url_for("employees"))
        return render_template("employees.html", items=Employee.query.order_by(Employee.name).all(), edit_item=item)

    @app.route("/pecas", methods=["GET", "POST"])
    @login_required
    def parts():
        if request.method == "POST":
            item = Part(
                name=request.form["name"],
                sku=request.form["sku"].upper(),
                stock=request.form["stock"],
                cost=request.form["cost"],
                price=request.form["price"],
            )
            db.session.add(item)
            db.session.commit()
            flash("Peca salva.", "success")
            return redirect(url_for("parts"))
        return render_template("parts.html", items=Part.query.order_by(Part.name).all(), edit_item=None)

    @app.route("/pecas/<int:item_id>/editar", methods=["GET", "POST"])
    @login_required
    def edit_part(item_id):
        item = db.get_or_404(Part, item_id)
        if request.method == "POST":
            item.name = request.form["name"]
            item.sku = request.form["sku"].upper()
            item.stock = request.form["stock"]
            item.cost = request.form["cost"]
            item.price = request.form["price"]
            db.session.commit()
            flash("Peca atualizada.", "success")
            return redirect(url_for("parts"))
        return render_template("parts.html", items=Part.query.order_by(Part.name).all(), edit_item=item)

    @app.route("/servicos", methods=["GET", "POST"])
    @login_required
    def services():
        if request.method == "POST":
            item = Service(
                name=request.form["name"],
                description=request.form.get("description"),
                base_price=request.form["base_price"],
                estimated_hours=request.form["estimated_hours"],
            )
            db.session.add(item)
            db.session.commit()
            flash("Servico salvo.", "success")
            return redirect(url_for("services"))
        return render_template("services.html", items=Service.query.order_by(Service.name).all(), edit_item=None)

    @app.route("/servicos/<int:item_id>/editar", methods=["GET", "POST"])
    @login_required
    def edit_service(item_id):
        item = db.get_or_404(Service, item_id)
        if request.method == "POST":
            item.name = request.form["name"]
            item.description = request.form.get("description")
            item.base_price = request.form["base_price"]
            item.estimated_hours = request.form["estimated_hours"]
            db.session.commit()
            flash("Servico atualizado.", "success")
            return redirect(url_for("services"))
        return render_template("services.html", items=Service.query.order_by(Service.name).all(), edit_item=item)

    @app.route("/ordens", methods=["GET", "POST"])
    @login_required
    def orders():
        if request.method == "POST":
            item = ServiceOrder(
                client_id=request.form["client_id"],
                car_id=request.form["car_id"],
                service_id=request.form["service_id"],
                employee_id=request.form["employee_id"],
                status=request.form["status"],
                hours_spent=request.form["hours_spent"],
                charged_value=request.form["charged_value"],
            )
            item.parts = Part.query.filter(Part.id.in_(request.form.getlist("part_ids"))).all()
            db.session.add(item)
            db.session.commit()
            flash("Ordem de servico salva.", "success")
            return redirect(url_for("orders"))
        return render_template(
            "orders.html",
            items=ServiceOrder.query.order_by(ServiceOrder.id.desc()).all(),
            clients=Client.query.order_by(Client.name).all(),
            cars=Car.query.order_by(Car.manufacturer, Car.model).all(),
            employees=Employee.query.order_by(Employee.name).all(),
            parts=Part.query.order_by(Part.name).all(),
            services=Service.query.order_by(Service.name).all(),
            statuses=["Aberta", "Em andamento", "Concluida", "Cancelada"],
            edit_item=None,
        )

    @app.route("/ordens/<int:item_id>/editar", methods=["GET", "POST"])
    @login_required
    def edit_order(item_id):
        item = db.get_or_404(ServiceOrder, item_id)
        if request.method == "POST":
            item.client_id = request.form["client_id"]
            item.car_id = request.form["car_id"]
            item.service_id = request.form["service_id"]
            item.employee_id = request.form["employee_id"]
            item.status = request.form["status"]
            item.hours_spent = request.form["hours_spent"]
            item.charged_value = request.form["charged_value"]
            item.parts = Part.query.filter(Part.id.in_(request.form.getlist("part_ids"))).all()
            db.session.commit()
            flash("Ordem de servico atualizada.", "success")
            return redirect(url_for("orders"))
        return render_template(
            "orders.html",
            items=ServiceOrder.query.order_by(ServiceOrder.id.desc()).all(),
            clients=Client.query.order_by(Client.name).all(),
            cars=Car.query.order_by(Car.manufacturer, Car.model).all(),
            employees=Employee.query.order_by(Employee.name).all(),
            parts=Part.query.order_by(Part.name).all(),
            services=Service.query.order_by(Service.name).all(),
            statuses=["Aberta", "Em andamento", "Concluida", "Cancelada"],
            edit_item=item,
        )

    @app.post("/excluir/<entity>/<int:item_id>")
    @login_required
    def delete(entity, item_id):
        models = {
            "clientes": Client,
            "carros": Car,
            "fabricantes": Manufacturer,
            "modelos": CarModel,
            "funcionarios": Employee,
            "pecas": Part,
            "servicos": Service,
            "ordens": ServiceOrder,
            "usuarios": User,
        }
        model = models.get(entity)
        if not model:
            flash("Tipo de registro invalido.", "error")
            return redirect(url_for("dashboard"))
        item = db.session.get(model, item_id)
        if item:
            if entity == "usuarios" and item.id == current_user.id:
                flash("Nao e possivel excluir o usuario logado.", "error")
                return redirect(request.referrer or url_for("users"))
            if entity == "usuarios" and not current_user.is_admin:
                abort(403)
            db.session.delete(item)
            db.session.commit()
            flash("Registro excluido.", "success")
        return redirect(request.referrer or url_for("dashboard"))


app = create_app()


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
