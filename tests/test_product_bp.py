import unittest
from app import app

class FlaskProductTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_products_list_page(self):
        """Тест сторінки списку всіх товарів"""
        response = self.client.get("/products")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Laptop".encode("utf-8"), response.data)
        self.assertIn("Phone".encode("utf-8"), response.data)

    def test_detail_product_page(self):
        """Тест детальної сторінки конкретного товару"""
        response = self.client.get("/products/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Laptop".encode("utf-8"), response.data)
        self.assertIn("1200".encode("utf-8"), response.data)

    def test_product_not_found(self):
        """Тест неіснуючого товару (повертає 404)"""
        response = self.client.get("/products/999")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()