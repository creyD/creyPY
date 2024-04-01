import unittest

from fastapi.routing import APIRoute

from creyPY.fastapi.app import generate_unique_id


class TestMyFunction(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
