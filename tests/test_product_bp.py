import io
import json
import os
import shutil
import tempfile
import unittest

from app import app
from app.products import storage

# мінімальний валідний PNG 1x1
PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


def product_data(**overrides):
    data = {
        "name": "Laptop",
        "content": "Потужний ноутбук для навчання",
        "price": "1200.50",
        "category": "electronics",
        "quantity": "5",
    }
    data.update(overrides)
    return data


def png(name="photo.png"):
    return (io.BytesIO(PNG_BYTES), name)


class ProductCrudTestCase(unittest.TestCase):
    """Модульні тести CRUD-операцій блюпринта products (TinyDB + Flask-WTF)."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old_config = dict(app.config)
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            PRODUCTS_DB=os.path.join(self.tmp, "data", "products.json"),
            PRODUCT_UPLOAD_FOLDER=os.path.join(self.tmp, "uploads"),
        )
        self.upload_dir = app.config["PRODUCT_UPLOAD_FOLDER"]
        self.client = app.test_client()

    def tearDown(self):
        app.config.clear()
        app.config.update(self.old_config)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ---------- helpers ----------

    def create(self, **overrides):
        return self.client.post("/product/add", data=product_data(**overrides),
                                content_type="multipart/form-data")

    def stored(self):
        with app.app_context():
            return storage.all_products()

    def text(self, response):
        return response.get_data(as_text=True)

    def upload_path(self, relative):
        return os.path.join(self.upload_dir, os.path.basename(relative))

    # ---------- Storage init ----------

    def test_new_storage_is_seeded_with_images(self):
        with app.app_context():
            storage.ensure_storage()
        products = self.stored()
        self.assertEqual([p["name"] for p in products], ["Laptop", "Phone", "PC"])
        for product in products:
            self.assertTrue(product["image"].startswith("uploads/"))
            self.assertTrue(os.path.isfile(self.upload_path(product["image"])))
        self.assertIn("/product/static/uploads/", self.text(self.client.get("/product")))

    # ---------- Create ----------

    def test_add_form_page(self):
        response = self.client.get("/product/add")
        self.assertEqual(response.status_code, 200)
        html = self.text(response)
        self.assertIn('enctype="multipart/form-data"', html)
        for field in ("name", "content", "price", "category", "quantity", "image"):
            self.assertIn(f'name="{field}"', html)

    def test_create_product_saves_to_tinydb_and_redirects(self):
        response = self.create()
        self.assertEqual(response.status_code, 302)  # PRG
        self.assertTrue(response.location.endswith("/product/1"))

        [product] = self.stored()
        self.assertEqual(product["id"], 1)
        self.assertEqual(product["name"], "Laptop")
        self.assertEqual(product["price"], 1200.5)
        self.assertEqual(product["quantity"], 5)
        self.assertEqual(product["category"], "electronics")
        self.assertIsNone(product["image"])
        self.assertTrue(product["created_at"])

        with open(app.config["PRODUCTS_DB"], encoding="utf-8") as f:
            self.assertIn("Laptop", json.dumps(json.load(f)))

        self.assertIn("додано", self.text(self.client.get(response.location)))  # flash

    def test_ids_are_generated_automatically(self):
        self.create(name="First")
        self.create(name="Second")
        self.assertEqual([p["id"] for p in self.stored()], [1, 2])

    def test_create_with_image_uses_uuid_filename(self):
        self.create(image=png("My Photo.PNG"))
        [product] = self.stored()
        self.assertTrue(product["image"].startswith("uploads/"))
        self.assertTrue(product["image"].endswith(".png"))
        self.assertNotIn("My Photo", product["image"])
        self.assertTrue(os.path.isfile(self.upload_path(product["image"])))

    def test_create_validation_errors(self):
        cases = [
            ({"name": "ab"}, "від 3 до 100"),
            ({"price": "-5"}, "додатною"),
            ({"price": "0"}, "додатною"),
            ({"price": "10.999"}, "двох знаків"),
            ({"quantity": "-1"}, "від&#39;ємною"),
            ({"category": ""}, "Оберіть категорію"),
            ({"content": ""}, "Додайте опис"),
        ]
        for overrides, error in cases:
            with self.subTest(overrides=overrides):
                response = self.create(**overrides)
                self.assertEqual(response.status_code, 200)
                self.assertIn(error, self.text(response))
                self.assertIn("Товар не збережено", self.text(response))
        self.assertEqual(self.stored(), [])

    def test_quantity_zero_is_allowed(self):
        self.assertEqual(self.create(quantity="0").status_code, 302)
        self.assertEqual(self.stored()[0]["quantity"], 0)

    def test_wrong_image_format_rejected(self):
        response = self.create(image=(io.BytesIO(b"GIF89a"), "anim.gif"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Дозволені лише PNG, JPG, JPEG", self.text(response))
        self.assertEqual(self.stored(), [])

    def test_too_big_image_rejected(self):
        big = io.BytesIO(b"\x89PNG" + b"0" * (2 * 1024 * 1024 + 10))
        response = self.create(image=(big, "big.png"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("більший за 2 МБ", self.text(response))
        self.assertEqual(self.stored(), [])

    # ---------- Read ----------

    def test_products_list_page(self):
        self.create(name="Python book", category="books", price="350.50", quantity="7")
        response = self.client.get("/product")
        self.assertEqual(response.status_code, 200)
        html = self.text(response)
        for text in ("Python book", "Книги", "350.50", "<strong>7</strong>", "Немає фото", "Додано:"):
            self.assertIn(text, html)

    def test_products_list_empty(self):
        self.assertIn("Товарів ще немає", self.text(self.client.get("/product")))

    def test_detail_product_page(self):
        self.create(image=png())
        response = self.client.get("/product/1")
        self.assertEqual(response.status_code, 200)
        html = self.text(response)
        self.assertIn("Потужний ноутбук для навчання", html)
        self.assertIn("1200.50", html)
        self.assertIn("/product/static/uploads/", html)

    def test_product_not_found(self):
        response = self.client.get("/product/999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("не знайдено", self.text(response))

    def test_missing_image_file_shows_placeholder(self):
        self.create(image=png())
        os.remove(self.upload_path(self.stored()[0]["image"]))
        self.assertIn("Зображення відсутнє", self.text(self.client.get("/product/1")))

    # ---------- Update ----------

    def test_edit_form_prefilled(self):
        self.create()
        html = self.text(self.client.get("/product/1/edit"))
        self.assertIn('value="Laptop"', html)
        self.assertIn('value="1200.50"', html)

    def test_edit_keeps_id_created_at_and_image(self):
        self.create(image=png())
        [before] = self.stored()
        response = self.client.post("/product/1/edit",
                                    data=product_data(name="Laptop Pro", price="1500.00", quantity="3"),
                                    content_type="multipart/form-data")
        self.assertEqual(response.status_code, 302)
        [after] = self.stored()
        self.assertEqual(after["name"], "Laptop Pro")
        self.assertEqual(after["price"], 1500.0)
        self.assertEqual(after["quantity"], 3)
        self.assertEqual(after["id"], before["id"])
        self.assertEqual(after["created_at"], before["created_at"])
        self.assertEqual(after["image"], before["image"])

    def test_edit_replaces_image(self):
        self.create(image=png())
        old = self.stored()[0]["image"]
        self.client.post("/product/1/edit", data=product_data(image=png("new.jpg")),
                         content_type="multipart/form-data")
        new = self.stored()[0]["image"]
        self.assertNotEqual(new, old)
        self.assertTrue(new.endswith(".jpg"))
        self.assertFalse(os.path.exists(self.upload_path(old)))
        self.assertTrue(os.path.exists(self.upload_path(new)))

    def test_edit_validation_error_not_saved(self):
        self.create()
        response = self.client.post("/product/1/edit", data=product_data(name="x"),
                                    content_type="multipart/form-data")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Зміни не збережено", self.text(response))
        self.assertEqual(self.stored()[0]["name"], "Laptop")

    def test_edit_not_found(self):
        self.assertEqual(self.client.get("/product/42/edit").status_code, 404)

    # ---------- Delete ----------

    def test_delete_product(self):
        self.create(image=png())
        image = self.stored()[0]["image"]
        response = self.client.post("/product/1/delete")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/product"))
        self.assertEqual(self.stored(), [])
        self.assertFalse(os.path.exists(self.upload_path(image)))
        self.assertIn("видалено", self.text(self.client.get("/product")))

    def test_delete_requires_post(self):
        self.create()
        self.assertEqual(self.client.get("/product/1/delete").status_code, 405)
        self.assertEqual(len(self.stored()), 1)

    def test_delete_not_found(self):
        response = self.client.post("/product/5/delete", follow_redirects=True)
        self.assertIn("не знайдено", self.text(response))

    def test_delete_without_csrf_token_rejected(self):
        self.create()
        app.config["WTF_CSRF_ENABLED"] = True
        self.client.post("/product/1/delete")
        self.assertEqual(len(self.stored()), 1)


if __name__ == "__main__":
    unittest.main()
