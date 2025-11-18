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
            "timestamp": pd.date_range(start="2025-07-01", periods=3, freq='D'),
            "station_code": ["123", "123", "123"],
            "price": [170.1, 171.5, 172.0],
            "fuel_type": ["P95" for _ in range(3)]
        })

        instance = MockDatabaseR.return_value
        instance.fetch_average_price.return_value = mock_df
        instance.unload.return_value = None
        
        response = self.client.get("/api/average_price_daily/?fuel_type=P95&start_date=2025-07-01&end_date=2025-07-31")
        assert response.status_code == 200
    
    @patch("fuel_backend.views.DatabaseR")
    def test_post_method_not_allowed(self, MockDatabaseR):
        instance = MockDatabaseR.return_value
        instance.fetch_average_price.return_value = pd.DataFrame()
        instance.unload.return_value = None
    
        response = self.client.post("/api/average_price_daily/?fuel_type=P95&start_date=2025-07-01&end_date=2025-07-31", {"fuel_type": "E10"})
        self.assertEqual(response.status_code, 405)

    @patch("fuel_backend.views.DatabaseR")
    def test_average_price_daily_view_success(self, MockDatabaseR):
        mock_df = pd.DataFrame({
            "timestamp": pd.date_range(start="2025-07-01", periods=3, freq='D'),
            "station_code": ["123", "123", "123"],
            "price": [170.1, 171.5, 172.0],
            "fuel_type": ["P95" for _ in range(3)]
        })

        instance = MockDatabaseR.return_value
        instance.fetch_average_price.return_value = mock_df
        instance.unload.return_value = None

        response = self.client.get("/api/average_price_daily/?fuel_type=P95&start_date=2025-07-01&end_date=2025-07-31")

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

        response = self.client.get("/api/average_price_daily/")

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
            "forecast_price": [180.0, 181.0],
            "fuel_type": ["P95" for _ in range(2)]
        })

        with patch("fuel_backend.views.average_future_price", return_value=future_df):
            response = self.client.get("/api/average_price_predict/?fuel_type=P95&start_date=2025-07-01&end_date=2025-07-31")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["avg_price"], 180.0)

    @patch("fuel_backend.views.DatabaseR")
    def test_average_price_daily_merge_past_and_future(self, MockDatabaseR):
        # Overlapping date: past should overwrite future
        mock_df = pd.DataFrame({
            "timestamp": pd.to_datetime(["2025-07-01", "2025-07-02"]),
            "station_code": ["123", "123"],
            "price": [170.0, 171.0],
            "fuel_type": ["P95" for _ in range(2)]
        })
        instance = MockDatabaseR.return_value
        instance.fetch_average_price.return_value = mock_df
        instance.unload.return_value = None

        future_df = pd.DataFrame({
            "timestamp": ["2025-07-02", "2025-07-03"],
            "forecast_price": [999.0, 172.0],
            "fuel_type": ["P95" for _ in range(2)]
        })

        with patch("fuel_backend.views.average_future_price", return_value=future_df):
            response = self.client.get("/api/average_price_daily/?fuel_type=P95&start_date=2025-07-01&end_date=2025-07-31")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(any(d["date"] == "2025-07-02" and d["avg_price"] == 171.0 for d in data))
            self.assertTrue(any(d["date"] == "2025-07-03" and d["avg_price"] == 172.0 for d in data))

class NearbyStationsViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("fuel_backend.views.DatabaseR")
    def test_nearby_stations_view_get_success(self, MockDatabaseR):
        #  Test with valid postcode and fuel type
        instance = MockDatabaseR.return_value

        instance.suburb_to_coordinates.return_value = (-33.8833, 151.1000)

        instance.get_nearby_suburbs.return_value = [
            {"suburb": "Strathfield", "postcode": "2135"},
            {"suburb": "Burwood", "postcode": "2134"},
        ]

        mock_df = pd.DataFrame([
            {
                "name": "7-Eleven Burwood", 
                "address": "Cnr Parramatta & Shaftsbury Rds, Burwood NSW 2134",  
                "postcode": "2134", 
                "latitude": -33.869406, 
                "longitude": 151.108603,
                "fuel_type": "P98",
                "price": 180.0,
                "timestamp": 1762923963
            }, {
                "name": "Coles Express Strathfield", 
                "address": "9 Albert Rd, Strathfield NSW 2135",  
                "postcode": "2135", 
                "latitude": -33.870803, 
                "longitude": 151.092355,
                "fuel_type": "P98",
                "price": 189.9,
                "timestamp": 1729293349
            },
        ])

        instance.fetch_data.return_value = mock_df
        instance.unload.return_value = None
        
        response = self.client.get("/api/nearby_stations/?fuel_type=P98&postcode=2134")
        data = response.json()

        assert response.status_code == 200
        assert data[0]["name"] == "7-Eleven Burwood"
        assert data[1]["name"] == "Coles Express Strathfield"
        assert data[0]["price"] == 180.0
        assert data[1]["price"] == 189.9

    @patch("fuel_backend.views.DatabaseR")
    def test_missing_postcode(self, MockDatabaseR):
        # Test request without postcode
        response = self.client.get("/api/nearby_stations/?fuel_type=P98")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    @patch("fuel_backend.views.DatabaseR")
    def test_no_nearby_suburbs(self, MockDatabaseR):
        # Test with postcode that yields no nearby suburbs
        instance = MockDatabaseR.return_value

        instance.suburb_to_coordinates.return_value = (-33.8833, 151.1)
        instance.get_nearby_suburbs.return_value = []

        response = self.client.get("/api/nearby_stations/?postcode=2134")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "No nearby suburbs found")

    @patch("fuel_backend.views.DatabaseR")
    def test_no_price_data(self, MockDatabaseR):
        # Test with valid postcode but no price data
        instance = MockDatabaseR.return_value

        instance.suburb_to_coordinates.return_value = (-33.8833, 151.1)
        instance.get_nearby_suburbs.return_value = [
            {"suburb": "Burwood", "postcode": "2134"}
        ]

        instance.fetch_data.return_value = pd.DataFrame()

        resp = self.client.get("/api/nearby_stations/?postcode=2134")
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()["error"], "No price data found")