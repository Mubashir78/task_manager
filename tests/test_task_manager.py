import os
import tempfile
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import database
import main
import models


class TaskManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.temp_db.close()

        database.engine = create_engine(
            f"sqlite:///{cls.temp_db.name}",
            connect_args={"check_same_thread": False},
        )
        database.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=database.engine,
        )
        models.Base.metadata.create_all(bind=database.engine)
        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "client"):
            cls.client.close()
        if hasattr(database, "SessionLocal"):
            database.SessionLocal.close_all()
        if hasattr(database, "engine"):
            database.engine.dispose()
        if os.path.exists(cls.temp_db.name):
            try:
                os.remove(cls.temp_db.name)
            except PermissionError:
                pass

    def setUp(self):
        db = database.SessionLocal()
        try:
            db.query(models.Task).delete()
            db.query(models.User).delete()
            db.commit()
        finally:
            db.close()


class TestPagination(TaskManagerTests):
    def setUp(self):
        super().setUp()
        db = database.SessionLocal()
        try:
            for index in range(12):
                user = models.User(name=f"User {index}", email=f"user{index}@example.com")
                db.add(user)
            db.commit()

            users = db.query(models.User).all()
            for index, user in enumerate(users):
                db.add(models.Task(title=f"Task {index}", description="desc", owner_id=user.id))
            db.commit()
        finally:
            db.close()

    def test_tasks_pagination(self):
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 10)

        paged_response = self.client.get("/tasks/", params={"skip": 5, "limit": 5})
        self.assertEqual(paged_response.status_code, 200)
        data = paged_response.json()
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0]["title"], "Task 5")

    def test_users_pagination(self):
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 10)

        paged_response = self.client.get("/users/", params={"skip": 5, "limit": 5})
        self.assertEqual(paged_response.status_code, 200)
        data = paged_response.json()
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0]["email"], "user5@example.com")


class TestCRUD(TaskManagerTests):
    def test_create_user(self):
        response = self.client.post("/users/", json={"name": "Alice", "email": "alice@example.com"})
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Alice")
        self.assertEqual(data["email"], "alice@example.com")
        self.assertIn("id", data)

    def test_create_duplicate_email(self):
        self.client.post("/users/", json={"name": "Alice", "email": "dup@example.com"})
        response = self.client.post("/users/", json={"name": "Bob", "email": "dup@example.com"})
        self.assertEqual(response.status_code, 409)

    def test_get_user_by_id(self):
        created = self.client.post("/users/", json={"name": "Alice", "email": "alice@example.com"}).json()
        response = self.client.get(f"/users/{created['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Alice")

    def test_get_user_not_found(self):
        response = self.client.get("/users/999")
        self.assertEqual(response.status_code, 404)

    def test_update_user(self):
        created = self.client.post("/users/", json={"name": "Alice", "email": "alice@example.com"}).json()
        response = self.client.put(f"/users/{created['id']}", json={"name": "Alicia"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Alicia")

    def test_update_user_not_found(self):
        response = self.client.put("/users/999", json={"name": "Ghost"})
        self.assertEqual(response.status_code, 404)

    def test_delete_user(self):
        created = self.client.post("/users/", json={"name": "Alice", "email": "alice@example.com"}).json()
        response = self.client.delete(f"/users/{created['id']}")
        self.assertEqual(response.status_code, 200)
        get_response = self.client.get(f"/users/{created['id']}")
        self.assertEqual(get_response.status_code, 404)

    def test_delete_user_not_found(self):
        response = self.client.delete("/users/999")
        self.assertEqual(response.status_code, 404)

    def test_create_task(self):
        user = self.client.post("/users/", json={"name": "Alice", "email": "alice@example.com"}).json()
        response = self.client.post("/tasks/", json={
            "title": "Test Task",
            "description": "A task",
            "owner_id": user["id"],
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], "Test Task")
        self.assertEqual(data["owner_id"], user["id"])

    def test_create_task_invalid_owner(self):
        response = self.client.post("/tasks/", json={
            "title": "Orphan Task",
            "owner_id": 999,
        })
        self.assertEqual(response.status_code, 400)

    def test_get_task_by_id(self):
        user = self.client.post("/users/", json={"name": "Alice", "email": "alice@example.com"}).json()
        task = self.client.post("/tasks/", json={"title": "Task", "owner_id": user["id"]}).json()
        response = self.client.get(f"/tasks/{task['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Task")

    def test_get_task_not_found(self):
        response = self.client.get("/tasks/999")
        self.assertEqual(response.status_code, 404)

    def test_update_task(self):
        user = self.client.post("/users/", json={"name": "Alice", "email": "alice@example.com"}).json()
        task = self.client.post("/tasks/", json={"title": "Old", "owner_id": user["id"]}).json()
        response = self.client.put(f"/tasks/{task['id']}", json={"title": "New", "completed": True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "New")
        self.assertTrue(response.json()["completed"])

    def test_update_task_not_found(self):
        response = self.client.put("/tasks/999", json={"title": "Ghost"})
        self.assertEqual(response.status_code, 404)

    def test_delete_task(self):
        user = self.client.post("/users/", json={"name": "Alice", "email": "alice@example.com"}).json()
        task = self.client.post("/tasks/", json={"title": "ToDelete", "owner_id": user["id"]}).json()
        response = self.client.delete(f"/tasks/{task['id']}")
        self.assertEqual(response.status_code, 200)
        get_response = self.client.get(f"/tasks/{task['id']}")
        self.assertEqual(get_response.status_code, 404)

    def test_delete_task_not_found(self):
        response = self.client.delete("/tasks/999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
