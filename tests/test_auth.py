from app.models.user import User
from app.utils.hash import hash_password


# ============================================================
# TEST: LOGIN SUCCESS
# ============================================================
def test_login_success(client, db_session):
    # Create test user
    user = User(
        first_name="Test",
        last_name="User",
        age=25,
        email="test@login.com",
        password=hash_password("password123"),
        role="superadmin",
    )
    db_session.add(user)
    db_session.commit()

    # Try login with correct password
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@login.com", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# ============================================================
# TEST: LOGIN WRONG PASSWORD
# ============================================================
def test_login_invalid_password(client, db_session):
    # Create test user
    user = User(
        first_name="Test2",
        last_name="User2",
        age=25,
        email="wrong@test.com",
        password=hash_password("correctpass"),
        role="superadmin",
    )
    db_session.add(user)
    db_session.commit()

    # Attempt login with WRONG password
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wrong@test.com", "password": "wrongpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


    assert response.status_code == 401
