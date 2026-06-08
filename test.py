import unittest
from uuid import UUID

from fastapi import HTTPException
from fastapi.routing import APIRoute
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from creyPY.fastapi.app import generate_unique_id
from creyPY.fastapi.crud import get_object_or_404
from creyPY.fastapi.models.base import Base


class MockDBClass(Base):
    def __init__(self, id):
        self.id = id


class TestMyFunction(unittest.TestCase):
    def setUp(self):
        # Create a SQLite in-memory database for testing
        engine = create_engine("sqlite:///:memory:")

        # Create a sessionmaker bound to this engine
        Session = sessionmaker(bind=engine)

        # Now you can use Session() to get a session bound to the engine
        self.db = Session()

        # create the table
        Base.metadata.create_all(engine)

    def test_generate_unique_id(self):
        # Test case 1: Route with no path parameters and GET method
        route1 = APIRoute(path="/users", methods={"GET"}, endpoint=lambda: None)
        assert generate_unique_id(route1) == "users_list"

        # Test case 2: Route with path parameters and POST method
        route2 = APIRoute(path="/users/{user_id}", methods={"POST"}, endpoint=lambda: None)
        assert generate_unique_id(route2) == "users_post"

        # Test case 3: Route with path parameters and multiple methods
        route3 = APIRoute(path="/users/{user_id}", methods={"GET", "PUT"}, endpoint=lambda: None)
        result = generate_unique_id(route3)
        assert result == "users_get" or result == "users_put"

        # Test case 4: Route with special characters in path
        route4 = APIRoute(
            path="/users/{user_id}/posts/{post_id}", methods={"DELETE"}, endpoint=lambda: None
        )
        assert generate_unique_id(route4) == "users_posts_delete"

        # Test case 5: Route with multiple path parameters and PATCH method
        route5 = APIRoute(
            path="/users/{user_id}/posts/{post_id}", methods={"PATCH"}, endpoint=lambda: None
        )
        assert generate_unique_id(route5) == "users_posts_patch"

        # Test case 6: Route with no path parameters and PUT method
        route6 = APIRoute(path="/users", methods={"PUT"}, endpoint=lambda: None)
        assert generate_unique_id(route6) == "users_put"

    def test_get_object_or_404_existing_object(self):
        # Arrange
        obj_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        obj = MockDBClass(id=obj_id)
        self.db.add(obj)
        self.db.commit()

        # Act
        result = get_object_or_404(MockDBClass, obj_id, self.db)

        # Assert
        assert result == obj

    def test_get_object_or_404_non_existing_object(self):
        # Arrange
        obj_id = UUID("123e4567-e89b-12d3-a456-426614174000")

        # Act & Assert
        with self.assertRaises(HTTPException) as exc_info:
            get_object_or_404(MockDBClass, obj_id, self.db)
        assert exc_info.exception.status_code == 404
        assert exc_info.exception.detail == "The object does not exist."


if __name__ == "__main__":
    unittest.main()
