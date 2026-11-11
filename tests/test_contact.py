import os
import shutil
import tempfile
import unittest

from app import create_app

app = create_app("testing")

VALID = {
    "name": "Olesia",
    "email": "olesia@example.com",
    "phone": "+380501234567",
    "subject": "support",
    "message": "Не працює кнопка оплати",
}


class ContactFormTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old_config = dict(app.config)
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            CONTACT_LOG=os.path.join(self.tmp, "contact.log"),
        )
        self.client = app.test_client()

    def tearDown(self):
        import logging
        for h in list(logging.getLogger("contact").handlers):
            logging.getLogger("contact").removeHandler(h)
            h.close()
        app.config.clear()
        app.config.update(self.old_config)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_contact_page_has_all_fields(self):
        response = self.client.get("/contact")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        for field in ("name", "email", "phone", "subject", "message"):
            self.assertIn(f'name="{field}"', html)
        self.assertIn("<select", html)
        self.assertIn("<textarea", html)

    def test_valid_form_is_logged_and_redirects(self):
        response = self.client.post("/contact", data=VALID)
        self.assertEqual(response.status_code, 302)  # Post/Redirect/Get
        self.assertTrue(response.location.endswith("/contact"))
        with open(app.config["CONTACT_LOG"], encoding="utf-8") as f:
            log = f.read()
        self.assertIn("olesia@example.com", log)
        self.assertIn("subject=support", log)
        page = self.client.get("/contact").get_data(as_text=True)
        self.assertIn("alert-success", page)

    def test_invalid_form_shows_errors(self):
        data = dict(VALID, email="bad", phone="123", subject="")
        response = self.client.post("/contact", data=data)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Введіть коректну email-адресу", html)
        self.assertIn("+380XXXXXXXXX", html)
        self.assertIn("оберіть тему", html)
        self.assertIn("alert-danger", html)
        self.assertFalse(os.path.exists(app.config["CONTACT_LOG"]))

    def test_csrf_token_required(self):
        app.config["WTF_CSRF_ENABLED"] = True
        html = self.client.get("/contact").get_data(as_text=True)
        self.assertIn('name="csrf_token"', html)
        response = self.client.post("/contact", data=VALID)
        self.assertEqual(response.status_code, 200)  # форма не пройшла валідацію
        self.assertIn("CSRF", response.get_data(as_text=True))
        self.assertFalse(os.path.exists(app.config["CONTACT_LOG"]))


if __name__ == "__main__":
    unittest.main()
