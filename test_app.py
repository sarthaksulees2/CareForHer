import pytest
import json
from app import app, db, User, Cycle
from werkzeug.security import generate_password_hash


# ================= SETUP =================

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def new_user(client):
    with app.app_context():
        user = User(
            name="Test User",
            email="test@example.com",
            phone="9999999999",
            password=generate_password_hash("Test@1234"),
            age=22,
            gender="Female",
            height=160.0,
            weight=55.0,
            cycle_length=28,
        )
        db.session.add(user)
        db.session.commit()
    return user


def login(client, email="test@example.com", password="Test@1234"):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)


# ================= HOME =================

class TestHome:

    def test_home_page_loads(self, client):
        res = client.get("/")
        assert res.status_code == 200

    def test_home_contains_brand(self, client):
        res = client.get("/")
        assert b"Care For Her" in res.data


# ================= REGISTER =================

class TestRegister:

    def test_register_page_loads(self, client):
        res = client.get("/register")
        assert res.status_code == 200

    def test_register_success(self, client):
        res = client.post("/register", data={
            "name": "Sarthak Sule",
            "email": "sarthak@example.com",
            "phone": "9876543210",
            "password": "Pass@1234",
            "age": "22",
            "gender": "Male",
            "height": "175",
            "weight": "70",
            "cycle_length": "28",
        }, follow_redirects=True)
        assert res.status_code == 200
        assert b"created successfully" in res.data or b"login" in res.data.lower()

    def test_register_duplicate_email(self, client, new_user):
        res = client.post("/register", data={
            "name": "Another User",
            "email": "test@example.com",
            "phone": "8888888888",
            "password": "Pass@1234",
            "age": "25",
            "gender": "Female",
            "height": "160",
            "weight": "55",
            "cycle_length": "28",
        }, follow_redirects=True)
        assert b"already registered" in res.data

    def test_register_duplicate_phone(self, client, new_user):
        res = client.post("/register", data={
            "name": "Another User",
            "email": "another@example.com",
            "phone": "9999999999",
            "password": "Pass@1234",
            "age": "25",
            "gender": "Female",
            "height": "160",
            "weight": "55",
            "cycle_length": "28",
        }, follow_redirects=True)
        assert b"already in use" in res.data


# ================= LOGIN =================

class TestLogin:

    def test_login_page_loads(self, client):
        res = client.get("/login")
        assert res.status_code == 200

    def test_login_success(self, client, new_user):
        res = login(client)
        assert res.status_code == 200
        assert b"dashboard" in res.data.lower() or b"Welcome" in res.data

    def test_login_wrong_password(self, client, new_user):
        res = client.post("/login", data={
            "email": "test@example.com",
            "password": "wrongpass"
        }, follow_redirects=True)
        assert b"Wrong email or password" in res.data

    def test_login_wrong_email(self, client):
        res = client.post("/login", data={
            "email": "notexist@example.com",
            "password": "Test@1234"
        }, follow_redirects=True)
        assert b"Wrong email or password" in res.data


# ================= LOGOUT =================

class TestLogout:

    def test_logout_redirects(self, client, new_user):
        login(client)
        res = client.get("/logout", follow_redirects=True)
        assert res.status_code == 200

    def test_logout_clears_session(self, client, new_user):
        login(client)
        client.get("/logout")
        res = client.get("/dashboard", follow_redirects=True)
        assert b"login" in res.data.lower()


# ================= DASHBOARD =================

class TestDashboard:

    def test_dashboard_requires_login(self, client):
        res = client.get("/dashboard", follow_redirects=True)
        assert b"login" in res.data.lower()

    def test_dashboard_loads_after_login(self, client, new_user):
        login(client)
        res = client.get("/dashboard")
        assert res.status_code == 200
        assert b"Test User" in res.data


# ================= TRACKER =================

class TestTracker:

    def test_tracker_requires_login(self, client):
        res = client.get("/tracker", follow_redirects=True)
        assert b"login" in res.data.lower()

    def test_tracker_page_loads(self, client, new_user):
        login(client)
        res = client.get("/tracker")
        assert res.status_code == 200

    def test_tracker_prediction(self, client, new_user):
        login(client)
        res = client.post("/tracker", data={
            "last_period": "2025-01-01",
            "cycle_length": "28"
        }, follow_redirects=True)
        assert res.status_code == 200
        assert b"2025-01-29" in res.data

    def test_tracker_saves_to_db(self, client, new_user):
        login(client)
        client.post("/tracker", data={
            "last_period": "2025-06-01",
            "cycle_length": "30"
        })
        with app.app_context():
            cycle = Cycle.query.filter_by(user_name="Test User").first()
            assert cycle is not None
            assert cycle.last_period == "2025-06-01"
            assert cycle.cycle_length == 30

    def test_tracker_uses_user_cycle_length_as_default(self, client, new_user):
        login(client)
        res = client.post("/tracker", data={
            "last_period": "2025-01-01",
        }, follow_redirects=True)
        assert res.status_code == 200
        # user.cycle_length = 28, so next = 2025-01-29
        assert b"2025-01-29" in res.data


# ================= PROFILE =================

class TestProfile:

    def test_profile_requires_login(self, client):
        res = client.get("/profile", follow_redirects=True)
        assert b"login" in res.data.lower()

    def test_profile_page_loads(self, client, new_user):
        login(client)
        res = client.get("/profile")
        assert res.status_code == 200
        assert b"Test User" in res.data

    def test_profile_update(self, client, new_user):
        login(client)
        res = client.post("/profile", data={
            "name": "Updated User",
            "email": "test@example.com",
            "phone": "9999999999",
            "age": "25",
            "height": "165",
            "weight": "60",
            "cycle_length": "30",
        }, follow_redirects=True)
        assert b"updated successfully" in res.data

    def test_profile_wrong_current_password(self, client, new_user):
        login(client)
        res = client.post("/profile", data={
            "name": "Test User",
            "email": "test@example.com",
            "phone": "9999999999",
            "age": "22",
            "height": "160",
            "weight": "55",
            "cycle_length": "28",
            "current_password": "wrongpass",
            "new_password": "NewPass@123",
            "confirm_password": "NewPass@123",
        }, follow_redirects=True)
        assert b"incorrect" in res.data

    def test_profile_password_mismatch(self, client, new_user):
        login(client)
        res = client.post("/profile", data={
            "name": "Test User",
            "email": "test@example.com",
            "phone": "9999999999",
            "age": "22",
            "height": "160",
            "weight": "55",
            "cycle_length": "28",
            "current_password": "Test@1234",
            "new_password": "NewPass@123",
            "confirm_password": "DifferentPass@123",
        }, follow_redirects=True)
        assert b"do not match" in res.data


# ================= CHATBOT =================

class TestChatbot:

    def test_chatbot_empty_message(self, client):
        res = client.post("/chatbot",
            data=json.dumps({"message": ""}),
            content_type="application/json"
        )
        assert res.status_code == 200
        data = json.loads(res.data)
        assert "reply" in data
        assert data["reply"] == "Please type a message."

    def test_chatbot_no_api_key(self, client):
        # gemini_client is None when no key is set in test env
        res = client.post("/chatbot",
            data=json.dumps({"message": "hi"}),
            content_type="application/json"
        )
        assert res.status_code == 200
        data = json.loads(res.data)
        assert "reply" in data


# ================= PROTECTED ROUTES =================

class TestProtectedRoutes:

    routes = ["/dashboard", "/tracker", "/profile", "/education", "/emergency", "/quiz", "/locator"]

    def test_all_protected_routes_redirect_to_login(self, client):
        for route in self.routes:
            res = client.get(route, follow_redirects=False)
            assert res.status_code == 302, f"{route} should redirect"
            assert "/login" in res.headers["Location"]


# ================= EDUCATION / EMERGENCY / QUIZ =================

class TestStaticPages:

    def test_education_loads(self, client, new_user):
        login(client)
        res = client.get("/education")
        assert res.status_code == 200

    def test_emergency_loads(self, client, new_user):
        login(client)
        res = client.get("/emergency")
        assert res.status_code == 200

    def test_quiz_loads(self, client, new_user):
        login(client)
        res = client.get("/quiz")
        assert res.status_code == 200
