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

    @patch("fuel_backend.views.DatabaseR")
    def test_average_price_daily_future_only(self, MockDatabaseR):
        # No past data, only future
        instance = MockDatabaseR.return_value
        instance.fetch_average_price.return_value = pd.DataFrame()
        instance.unload.return_value = None

        future_df = pd.DataFrame({
            "timestamp": ["2024-07-01", "2024-07-02"],
            "forecast_price": [180.0, 181.0]
        })

        with patch("fuel_backend.views.average_future_price", return_value=future_df):
            response = self.client.get("/api/average_price_daily/?fuel_type=E10")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["avg_price"], 180.0)

    @patch("fuel_backend.views.DatabaseR")
    def test_average_price_daily_merge_past_and_future(self, MockDatabaseR):
        # Overlapping date: past should overwrite future
        mock_df = pd.DataFrame({
            "timestamp": pd.to_datetime(["2024-07-01", "2024-07-02"]),
            "station_code": ["123", "123"],
            "price": [170.0, 171.0]
        })
        instance = MockDatabaseR.return_value
        instance.fetch_average_price.return_value = mock_df
        instance.unload.return_value = None

        future_df = pd.DataFrame({
            "timestamp": ["2024-07-02", "2024-07-03"],
            "forecast_price": [999.0, 172.0]
        })

        with patch("fuel_backend.views.average_future_price", return_value=future_df):
            response = self.client.get("/api/average_price_daily/?fuel_type=E10")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            # 2024-07-02 should have the past value, not 999.0
            self.assertTrue(any(d["date"] == "2024-07-02" and d["avg_price"] == 171.0 for d in data))
            self.assertTrue(any(d["date"] == "2024-07-03" and d["avg_price"] == 172.0 for d in data))