from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
import string

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

random_username = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
random_password = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
test_file = 'tests/test_data/logo.jpeg'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_register():
    r = client.post('/signup', json={
        'username': random_username,
        'hashed_password': random_password
    })
    assert r.status_code == 200


def test_register_fail_username_exists():
    r = client.post('/signup', json={
        'username': random_username,
        'hashed_password': random_password
    })
    assert r.status_code == 400


headers = {"Authorization": ""}


def test_authentication():
    data = {"username": random_username, "password": random_password}
    r = client.post("/token", data=data)
    auth_token = r.json()["access_token"]
    headers["Authorization"] = f"Bearer {auth_token}"
    assert r.status_code == 200


def test_fail_authentication():
    data = {"username": random_username, "password": "random_password"}
    r = client.post("/token", data=data)
    assert r.status_code == 401


def test_unauthorized_upload_file():
    with open(test_file, 'rb') as f:
        files = {"frames": ('logo.jpeg', f, 'multipart/form-data')}
        response = client.post('/frames/', files=files)
    assert response.status_code == 401


def test_upload_file():
    with open(test_file, 'rb') as f:
        files = {"frames": ('logo.jpeg', f, 'multipart/form-data')}
        response = client.post('/frames/', files=files, headers=headers)
    assert response.status_code == 201


def test_upload_no_file():
    files = []
    response = client.post('/frames/', files=files, headers=headers)
    assert response.status_code == 422


def test_upload_several_files():
    files = [
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
    ]
    response = client.post('/frames/', files=files, headers=headers)
    assert response.status_code == 201


def test_upload_too_many_files():
    files = [
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('foo.png', open(test_file, 'rb'), 'image/png')),
        ("frames", ('bar.png', open(test_file, 'rb'), 'image/png'))
    ]
    response = client.post('/frames/', files=files, headers=headers)
    assert response.status_code == 400


def test_unauthorized_get_file():
    response = client.get(f"/frames/?id=1")
    assert response.status_code == 401, response.text


def test_get_file():
    response = client.get(f"/frames/?id=1", headers=headers)
    assert response.status_code == 200, response.text


def test_get_several_file():
    response = client.get(f"/frames/?id=1&id=3", headers=headers)
    assert response.status_code == 200, response.text


def test_unauthorized_delete_file():
    response = client.delete(f"/frames/?id=1")
    assert response.status_code == 401, response.text


def test_delete_file():
    response = client.delete(f"/frames/?id=1", headers=headers)
    assert response.status_code == 204, response.text


def test_delete_several_file():
    response = client.get(f"/frames/?id=1&id=3", headers=headers)
    assert response.status_code == 200, response.text
