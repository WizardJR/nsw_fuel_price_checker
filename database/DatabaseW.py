from Fetcher import Fetcher
from DatabaseR import DatabaseR
import pandas as pd
from datetime import datetime
import pytz
import re

class DatabaseW(DatabaseR):
    def __init__(self, configs):
        super().__init__(configs['db_name'])
        self.start_timestamp = configs['start_timestamp']
        self.fetcher = Fetcher(configs['AUTHORIZATION_HEADER'], configs['API_KEY'])

    def update_db(self):
        all_prices = self.fetcher.fetch_all_v1_data()
        self.save_stations_to_db(all_prices['stations'])
        self.save_prices_to_db(all_prices['prices'])

        new_prices = self.fetcher.fetch_new_v1_data()
        self.save_stations_to_db(new_prices['stations'])
        self.save_prices_to_db(new_prices['prices'])

    def save_prices_to_db(self, prices_data):
        cursor = self.cursor
        prices_df = pd.DataFrame(prices_data)
        create_prices_table_query = """
        CREATE TABLE IF NOT EXISTS prices (
            station_code TEXT,
            fuel_type TEXT,
            price REAL,
            timestamp INTEGER,
            PRIMARY KEY (station_code, fuel_type, timestamp),
            FOREIGN KEY (station_code) REFERENCES stations (station_code)
        )
        """
        cursor.execute(create_prices_table_query)

        timezone = pytz.timezone("UTC")

        for _, row in prices_df.iterrows():
            insert_query = """
            INSERT INTO prices (station_code, fuel_type, price, timestamp) 
            VALUES (?, ?, ?, ?)
            """
            timestamp = self.convert_to_unix_timestamp(row['lastupdated'], timezone)
            if not self.price_exists(cursor, row['stationcode'], row['fueltype'], timestamp) and timestamp > self.start_timestamp:
                cursor.execute(insert_query, (
                    row['stationcode'],
                    row['fueltype'],
                    row['price'],
                    timestamp
                ))
            else:
                continue
        self.conn.commit()

    def price_exists(self, cursor, station_code, fuel_type, timestamp):
        cursor.execute("""
        SELECT 1 FROM prices 
        WHERE station_code = ? AND fuel_type = ? AND timestamp = ?
        """, (station_code, fuel_type, timestamp))
        return cursor.fetchone() is not None

    def save_stations_to_db(self, stations_data):
        cursor = self.cursor
        stations_df = pd.json_normalize(stations_data)
        create_stations_table_query = """
        CREATE TABLE IF NOT EXISTS stations (
            brand_id TEXT,
            station_id TEXT,
            brand TEXT,
            station_code TEXT PRIMARY KEY,
            name TEXT,
            address TEXT,
            latitude REAL,
            longitude REAL,
            is_adblue_available BOOLEAN
            postcode TEXT
        )
        """
        cursor.execute(create_stations_table_query)
        cursor.execute("PRAGMA table_info(stations);")
        columns = [info[1] for info in cursor.fetchall()]
        if 'postcode' not in columns:
            cursor.execute("ALTER TABLE stations ADD COLUMN postcode TEXT")

        for _, row in stations_df.iterrows():
            postcode = self.extract_postcode(row['address'])
            insert_query = """
            INSERT INTO stations (brand_id, station_id, brand, station_code, name, address, latitude, longitude, is_adblue_available, postcode) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            if not self.station_exists(cursor, row['code']):
                cursor.execute(insert_query, (
                    row['brandid'],
                    row['stationid'],
                    row['brand'],
                    row['code'],
                    row['name'],
                    row['address'],
                    row['location.latitude'],
                    row['location.longitude'],
                    row['isAdBlueAvailable'],
                    postcode
                ))
            else:
                continue
        self.conn.commit()

    def station_exists(self, cursor, station_code):
        cursor.execute("""
        SELECT 1 FROM stations 
        WHERE station_code = ?
        """, (station_code,))
        return cursor.fetchone() is not None
    
    def convert_to_unix_timestamp(self, date_str, timezone):
        dt = datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
        localized_dt = timezone.localize(dt)
        unix_timestamp = int(localized_dt.timestamp())
        return unix_timestamp

    def extract_postcode(self, address):
        matches = re.findall(r'\b\d{4}\b', address)
        return matches[-1] if matches else None
