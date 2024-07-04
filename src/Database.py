import sqlite3
import pandas as pd
from datetime import datetime
import pytz
from Fetcher import Fetcher

class Database:
    def __init__(self, configs):
        self.start_timestamp = configs['start_timestamp']
        self.conn = sqlite3.connect(configs['db_name'])
        self.cursor = self.conn.cursor()
        self.fetcher = Fetcher(configs['AUTHORIZATION_HEADER'])
        
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
            station_id TEXT PRIMARY KEY,
            brand TEXT,
            station_code TEXT,
            name TEXT,
            address TEXT,
            latitude REAL,
            longitude REAL,
            is_adblue_available BOOLEAN
        )
        """
        cursor.execute(create_stations_table_query)

        for _, row in stations_df.iterrows():
            insert_query = """
            INSERT INTO stations (brand_id, station_id, brand, station_code, name, address, latitude, longitude, is_adblue_available) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            if not self.station_exists(cursor, row['stationid']):
                cursor.execute(insert_query, (
                    row['brandid'],
                    row['stationid'],
                    row['brand'],
                    row['code'],
                    row['name'],
                    row['address'],
                    row['location.latitude'],
                    row['location.longitude'],
                    row['isAdBlueAvailable']
                ))
            else:
                continue
        self.conn.commit()

    def station_exists(self, cursor, station_id):
        cursor.execute("""
        SELECT 1 FROM stations 
        WHERE station_id = ?
        """, (station_id,))
        return cursor.fetchone() is not None

    def unload(self):
        self.conn.commit()
        self.conn.close()

    def fetch_data(self, fuel_type, start_date=None, end_date=None, station_code=None):
        query = """
        SELECT 
            stations.name, 
            stations.address, 
            prices.fuel_type, 
            prices.price, 
            prices.timestamp, 
            prices.station_code
        FROM 
            stations
        JOIN 
            prices ON stations.station_code = prices.station_code
        """

        conditions = []
        params = []

        if fuel_type:
            conditions.append("prices.fuel_type = ?")
            params.append(fuel_type)
        
        if start_date and end_date:
            conditions.append("date(prices.timestamp, 'unixepoch') BETWEEN date(?, 'unixepoch') AND date(?, 'unixepoch')")
            params.append(start_date)
            params.append(end_date)
        
        if station_code:
            placeholders = ','.join('?' for _ in station_code)
            conditions.append(f"prices.station_code IN ({placeholders})")
            params.extend(station_code)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        df = pd.read_sql_query(query, self.conn, params=params)
        return df

    def convert_to_unix_timestamp(self, date_str, timezone):
        dt = datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
        localized_dt = timezone.localize(dt)
        unix_timestamp = int(localized_dt.timestamp())
        return unix_timestamp