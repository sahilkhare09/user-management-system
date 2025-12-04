from app.models.user import User
from app.utils.hash import hash_password


# ============================================================
# CREATE USER
# ============================================================
def test_create_user(client, superadmin_token):
    new_user = {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "email": "john@doe.com",
        "password": "secret123",
        "role": "admin",
    }

    response = client.post(
        "/api/v1/users",
        json=new_user,
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )

    assert response.status_code in [200, 201]
    assert response.json()["email"] == "john@doe.com"


# ============================================================
# GET ALL USERS
# ============================================================
def test_get_all_users(client, superadmin_token):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {superadmin_token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

# ============================================================
# GET SINGLE USER
# ============================================================
def test_get_single_user(client, db_session, superadmin_token):
    # Create user in DB
    user = User(
        first_name="Unique",
        last_name="Test",
        email="unique@test.com",
        age=22,
        password=hash_password("pass123"),
        role="employee",
    )
    db_session.add(user)
    db_session.commit()

    # Fetch user
    response = client.get(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "unique@test.com"


# ============================================================
# UPDATE USER
# ============================================================
def test_update_user(client, db_session, superadmin_token):
    # Create user
    user = User(
        first_name="Old",
        last_name="Name",
        age=22,
        email="oldname@test.com",
        password=hash_password("pass123"),
        role="employee",
    )
    db_session.add(user)
    db_session.commit()

    updated_data = {
        "first_name": "New",
        "last_name": "Name",
        "age": 22,
        "email": "oldname@test.com",
        "role": "employee",
    }

    response = client.put(
        f"/api/v1/users/{user.id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {superadmin_token}"}
    )


    assert response.status_code == 200
    assert response.json()["first_name"] == "New"


# ============================================================
# DELETE USER
# ============================================================
def test_delete_user(client, db_session, superadmin_token):
    user = User(
        first_name="Delete",
        last_name="Me",
        age=20,
        email="delete@me.com",
        password=hash_password("pass123"),
        role="employee",
    )
    db_session.add(user)
    db_session.commit()

    # Delete user
    response = client.delete(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {superadmin_token}"}
    )


    assert response.status_code == 200

    # Verify user deleted
    response = client.get(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )

    assert response.status_code == 404
