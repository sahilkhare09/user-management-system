import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.db import Base
from app.models.user import User
from app.utils.hash import hash_password
from app.services.auth_service import create_access_token
from uuid import uuid4


SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_db():
        try:
            yield db_session
        finally:
            pass

    from app.database.db import get_db
    app.dependency_overrides[get_db] = override_db

    return TestClient(app)


@pytest.fixture
def superadmin_token(db_session):
    user = User(
        id=uuid4(),
        first_name="Admin",
        last_name="User",
        age=30,
        email=f"admin_{uuid4()}@test.com",
        password=hash_password("admin123"),
        role="superadmin",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token({"sub": str(user.id)})

    return token
