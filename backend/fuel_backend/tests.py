from django.test import TestCase, Client
from unittest.mock import patch
import pandas as pd
from datetime import datetime

# Create your tests here.
class AveragePriceViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("fuel_backend.views.DatabaseR")
    def test_average_price_daily_view_get(self, MockDatabaseR):
        mock_df = pd.DataFrame({
            "timestamp": pd.date_range(start="2024-06-01", periods=3, freq='D'),
            "station_code": ["123", "123", "123"],
            "price": [170.1, 171.5, 172.0]
        })

        instance = MockDatabaseR.return_value
        instance.fetch_average_price.return_value = mock_df
        instance.unload.return_value = None
        
        response = self.client.get("/api/average_price_daily/")
        assert response.status_code == 200
    
    @patch("fuel_backend.views.DatabaseR")
    def test_post_method_not_allowed(self, MockDatabaseR):
        instance = MockDatabaseR.return_value
        instance.fetch_average_price.return_value = pd.DataFrame()
        instance.unload.return_value = None
    
        response = self.client.post("/api/average_price_daily/", {"fuel_type": "E10"})
        self.assertEqual(response.status_code, 405)

    @patch("fuel_backend.views.DatabaseR")
    def test_average_price_daily_view_success(self, MockDatabaseR):
        mock_df = pd.DataFrame({
            "timestamp": pd.date_range(start="2024-06-01", periods=3, freq='D'),
            "station_code": ["123", "123", "123"],
            "price": [170.1, 171.5, 172.0]
        })

        instance = MockDatabaseR.return_value
        instance.fetch_average_price.return_value = mock_df
        instance.unload.return_value = None

        response = self.client.get("/api/average_price_daily/?fuel_type=E10")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 3)
        self.assertIn("date", response.json()[0])
        self.assertIn("avg_price", response.json()[0])

    @patch("fuel_backend.views.DatabaseR")
    def test_average_price_daily_empty_database(self, MockDatabaseR):
        instance = MockDatabaseR.return_value
        instance.fetch_average_price.return_value = pd.DataFrame()
        instance.unload.return_value = None

        response = self.client.get("/api/average_price_daily/?fuel_type=E10")

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())