import os
import tempfile
import unittest

from webapp import app


class OmisbotsAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.original_store = os.environ.get("OMISBOTS_STORE_PATH")
        fd, temp_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.environ["OMISBOTS_STORE_PATH"] = temp_path

    def tearDown(self):
        if self.original_store is None:
            os.environ.pop("OMISBOTS_STORE_PATH", None)
        else:
            os.environ["OMISBOTS_STORE_PATH"] = self.original_store

    def test_home_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_create_bot_persists_to_store_file(self):
        response = self.client.post(
            "/dashboard/create-bot",
            data={
                "name": "Growth Pilot",
                "website": "https://pilot.example.com",
                "template": "Sales Assistant",
            },
            follow_redirects=False,
        )

        self.assertIn(response.status_code, (200, 302))
        store_path = os.environ["OMISBOTS_STORE_PATH"]
        self.assertTrue(os.path.exists(store_path))

        with open(store_path, "r", encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("Growth Pilot", content)


if __name__ == "__main__":
    unittest.main()
