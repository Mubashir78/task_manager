import os
import tempfile
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import database
import main
import models


class PaginationTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
