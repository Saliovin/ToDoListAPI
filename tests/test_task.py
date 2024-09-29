from fastapi.testclient import TestClient
import pytest
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


@pytest.fixture
def setup():
    SQLALCHEMY_DATABASE_URL = "sqlite://"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
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


def test_get_tasks(setup):
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []

    response = client.get("/tasks/rank")
    assert response.status_code == 200
    assert response.json() == []


def test_post_task(setup):
    response = client.post(
        "/tasks/",
        json={"task_detail": "test"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "task_detail": "test",
        "id": 1,
        "order": 1.0,
        "numerator": 1,
        "denominator": 1,
        "rank": "i",
    }


def test_put_task(setup):
    client.post(
        "/tasks/",
        json={"task_detail": "test"},
    )
    response = client.put(
        "/tasks/1",
        json={"task_detail": "test_update"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "task_detail": "test_update",
        "id": 1,
        "order": 1.0,
        "numerator": 1,
        "denominator": 1,
        "rank": "i",
    }


def test_delete_task(setup):
    client.post(
        "/tasks/",
        json={"task_detail": "test"},
    )
    response = client.delete("/tasks/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted successfully"}
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []


def test_move_task(setup):
    client.post(
        "/tasks/",
        json={"task_detail": "test"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test2"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test3"},
    )
    response = client.put(
        "/tasks/move/3",
        json={"prev_task_id": 1, "next_task_id": 2},
    )
    assert response.status_code == 200
    assert response.json() == {
        "task_detail": "test3",
        "id": 3,
        "order": 1.5,
        "numerator": 3,
        "denominator": 2,
        "rank": "m",
    }

    expected = [
        {
            "denominator": 1,
            "id": 1,
            "numerator": 1,
            "order": 1.0,
            "rank": "i",
            "task_detail": "test",
        },
        {
            "denominator": 2,
            "id": 3,
            "numerator": 3,
            "order": 1.5,
            "rank": "m",
            "task_detail": "test3",
        },
        {
            "denominator": 1,
            "id": 2,
            "numerator": 2,
            "order": 2.0,
            "rank": "q",
            "task_detail": "test2",
        },
    ]

    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == expected

    response = client.get("/tasks/rank")
    assert response.status_code == 200
    assert response.json() == expected


def test_move_task_start(setup):
    client.post(
        "/tasks/",
        json={"task_detail": "test"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test2"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test3"},
    )
    response = client.put(
        "/tasks/move/3",
        json={"next_task_id": 1},
    )
    assert response.status_code == 200
    assert response.json() == {
        "task_detail": "test3",
        "id": 3,
        "order": 0.5,
        "numerator": 1,
        "denominator": 2,
        "rank": "L",
    }

    expected = [
        {
            "denominator": 2,
            "id": 3,
            "numerator": 1,
            "order": 0.5,
            "rank": "L",
            "task_detail": "test3",
        },
        {
            "denominator": 1,
            "id": 1,
            "numerator": 1,
            "order": 1.0,
            "rank": "i",
            "task_detail": "test",
        },
        {
            "denominator": 1,
            "id": 2,
            "numerator": 2,
            "order": 2.0,
            "rank": "q",
            "task_detail": "test2",
        },
    ]

    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == expected

    response = client.get("/tasks/rank")
    assert response.status_code == 200
    assert response.json() == expected


def test_move_task_end(setup):
    client.post(
        "/tasks/",
        json={"task_detail": "test"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test2"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test3"},
    )
    response = client.put(
        "/tasks/move/2",
        json={"prev_task_id": 3},
    )
    assert response.status_code == 200
    assert response.json() == {
        "task_detail": "test2",
        "id": 2,
        "order": 4.0,
        "numerator": 4,
        "denominator": 1,
        "rank": "w",
    }

    expected = [
        {
            "denominator": 1,
            "id": 1,
            "numerator": 1,
            "order": 1.0,
            "rank": "i",
            "task_detail": "test",
        },
        {
            "denominator": 1,
            "id": 3,
            "numerator": 3,
            "order": 3.0,
            "rank": "u",
            "task_detail": "test3",
        },
        {
            "denominator": 1,
            "id": 2,
            "numerator": 4,
            "order": 4.0,
            "rank": "w",
            "task_detail": "test2",
        },
    ]

    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == expected

    response = client.get("/tasks/rank")
    assert response.status_code == 200
    assert response.json() == expected


def test_move_task_jump(setup):
    client.post(
        "/tasks/",
        json={"task_detail": "test"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test2"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test3"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test4"},
    )
    response = client.put(
        "/tasks/move/1",
        json={"prev_task_id": 3, "next_task_id": 4},
    )
    assert response.status_code == 200
    assert response.json() == {
        "task_detail": "test",
        "id": 1,
        "order": 3.5,
        "numerator": 7,
        "denominator": 2,
        "rank": "v",
    }

    expected = [
        {
            "denominator": 1,
            "id": 2,
            "numerator": 2,
            "order": 2.0,
            "rank": "q",
            "task_detail": "test2",
        },
        {
            "denominator": 1,
            "id": 3,
            "numerator": 3,
            "order": 3.0,
            "rank": "u",
            "task_detail": "test3",
        },
        {
            "denominator": 2,
            "id": 1,
            "numerator": 7,
            "order": 3.5,
            "rank": "v",
            "task_detail": "test",
        },
        {
            "denominator": 1,
            "id": 4,
            "numerator": 4,
            "order": 4.0,
            "rank": "w",
            "task_detail": "test4",
        },
    ]

    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == expected

    response = client.get("/tasks/rank")
    assert response.status_code == 200
    assert response.json() == expected


def test_move_task_multiple(setup):
    client.post(
        "/tasks/",
        json={"task_detail": "test"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test2"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test3"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test4"},
    )

    ctr = 0
    while ctr < 51:
        if ctr % 2 == 0:
            response = client.put(
                "/tasks/move/3",
                json={"prev_task_id": 1, "next_task_id": 2},
            )
        else:
            response = client.put(
                "/tasks/move/3",
                json={"prev_task_id": 2, "next_task_id": 4},
            )
        assert response.status_code == 200
        ctr += 1
    assert response.json() == {
        "task_detail": "test3",
        "id": 3,
        "order": 1.5,
        "numerator": 3,
        "denominator": 2,
        "rank": "m",
    }

    expected = [
        {
            "denominator": 1,
            "id": 1,
            "numerator": 1,
            "order": 1.0,
            "rank": "i",
            "task_detail": "test",
        },
        {
            "denominator": 2,
            "id": 3,
            "numerator": 3,
            "order": 1.5,
            "rank": "m",
            "task_detail": "test3",
        },
        {
            "denominator": 1,
            "id": 2,
            "numerator": 2,
            "order": 2.0,
            "rank": "q",
            "task_detail": "test2",
        },
        {
            "denominator": 1,
            "id": 4,
            "numerator": 4,
            "order": 4.0,
            "rank": "w",
            "task_detail": "test4",
        },
    ]

    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == expected

    response = client.get("/tasks/rank")
    assert response.status_code == 200
    assert response.json() == expected


def test_move_task_deep(setup):
    client.post(
        "/tasks/",
        json={"task_detail": "test"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test2"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test3"},
    )
    client.post(
        "/tasks/",
        json={"task_detail": "test4"},
    )

    ctr = 0
    while ctr < 101:
        if ctr % 2 == 0:
            response = client.put(
                "/tasks/move/3",
                json={"prev_task_id": 1, "next_task_id": 2},
            )
        else:
            response = client.put(
                "/tasks/move/2",
                json={"prev_task_id": 1, "next_task_id": 3},
            )
        assert response.status_code == 200
        ctr += 1

    expected = [
        {
            "denominator": 1,
            "id": 1,
            "numerator": 1,
            "order": 1.0,
            "rank": "i",
            "task_detail": "test",
        },
        {
            "denominator": 102,
            "id": 3,
            "numerator": 103,
            "order": 1.0098039215686274,
            "rank": "i0000000000000000B",
            "task_detail": "test3",
        },
        {
            "denominator": 101,
            "id": 2,
            "numerator": 102,
            "order": 1.00990099009901,
            "rank": "i0000000000000000U",
            "task_detail": "test2",
        },
        {
            "denominator": 1,
            "id": 4,
            "numerator": 4,
            "order": 4.0,
            "rank": "w",
            "task_detail": "test4",
        },
    ]

    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == expected

    response = client.get("/tasks/rank")
    assert response.status_code == 200
    assert response.json() == expected
