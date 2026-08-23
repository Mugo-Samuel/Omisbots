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
        user_fd, user_path = tempfile.mkstemp(suffix=".json")
        os.close(user_fd)
        os.environ["OMISBOTS_USERS_PATH"] = user_path

    def tearDown(self):
        if self.original_store is None:
            os.environ.pop("OMISBOTS_STORE_PATH", None)
        else:
            os.environ["OMISBOTS_STORE_PATH"] = self.original_store
        os.environ.pop("OMISBOTS_USERS_PATH", None)

    def test_home_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_chat_accepts_form_and_json_requests(self):
        form_response = self.client.post("/chat", data={"message": "What does Omisbots do?"})
        json_response = self.client.post("/chat", json={"message": "Can you connect Gmail to my CRM?"})
        self.assertEqual(form_response.status_code, 200)
        self.assertEqual(json_response.status_code, 200)
        self.assertIn("Omisbots", form_response.get_json()["reply"])
        self.assertIn("Gmail", json_response.get_json()["reply"])

    def test_dashboard_requires_authentication(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth", response.location)

    def test_signup_login_and_logout(self):
        response = self.client.post(
            "/auth",
            data={"mode": "signup", "name": "Test User", "email": "test@example.com", "password": "secret123"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)

        dashboard = self.client.get("/dashboard")
        self.assertEqual(dashboard.status_code, 200)

        self.client.post("/logout")
        self.assertEqual(self.client.get("/dashboard").status_code, 302)

    def test_agent_builder_test_and_deploy(self):
        self.client.post(
            "/auth",
            data={"mode": "signup", "name": "Agent Builder", "email": "agent@example.com", "password": "secret123"},
        )
        response = self.client.post("/api/agents", json={"request": "Create an agent that manages my emails and updates my CRM."})
        self.assertEqual(response.status_code, 201)
        agent_id = response.get_json()["agent"]["id"]

        test_response = self.client.post(f"/api/agents/{agent_id}/test")
        deploy_response = self.client.post(f"/api/agents/{agent_id}/deploy")
        self.assertEqual(test_response.status_code, 200)
        self.assertEqual(deploy_response.status_code, 200)
        self.assertEqual(deploy_response.get_json()["agent"]["status"], "Running")

    def test_automation_generates_safe_workflow_definition(self):
        self.client.post(
            "/auth",
            data={"mode": "signup", "name": "Automation Builder", "email": "automation@example.com", "password": "secret123"},
        )
        response = self.client.post("/api/automations", json={"description": "When a website lead arrives, qualify it and notify me."})
        self.assertEqual(response.status_code, 201)
        workflow = response.get_json()["automation"]["workflow"]
        self.assertEqual(workflow["active"], False)
        self.assertIn("CRM_CREDENTIAL", str(workflow))
        self.assertNotIn("api_key", str(workflow).lower())

    def test_create_bot_persists_to_store_file(self):
        self.client.post(
            "/auth",
            data={"mode": "signup", "name": "Bot Builder", "email": "builder@example.com", "password": "secret123"},
        )
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
