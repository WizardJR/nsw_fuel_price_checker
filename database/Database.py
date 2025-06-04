import sqlite3
import pandas as pd
from datetime import datetime
import pytz
from Fetcher import Fetcher
import re
import geopy
from geopy.distance import geodesic

class Database:
    def __init__(self, configs):
        self.start_timestamp = configs['start_timestamp']
        self.conn = sqlite3.connect(configs['db_name'])
        self.cursor = self.conn.cursor()
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

    def unload(self):
        self.conn.commit()
        self.conn.close()
    
    def fetch_stations(self, station_codes=None, brand_ids=None, station_ids=None, postcode=None):
        if not (station_codes or brand_ids or station_ids or postcode):
            raise ValueError("At least one filter criteria must be provided")
        query = """
        SELECT * FROM stations WHERE 1=1
        """
        params = []

        if station_codes:
            placeholders = ','.join('?' for _ in station_codes)
            query += f" AND station_code IN ({placeholders})"
            params.extend(station_codes)

        if brand_ids:
            placeholders = ','.join('?' for _ in brand_ids)
            query += f" AND brand_id IN ({placeholders})"
            params.extend(brand_ids)

        if station_ids:
            placeholders = ','.join('?' for _ in station_ids)
            query += f" AND station_id IN ({placeholders})"
            params.extend(station_ids)

        if postcode:
            placeholders = ','.join('?' for _ in postcode)
            query += f" AND stations.postcode IN ({placeholders})"
            params.extend(postcode)

        df = pd.read_sql_query(query, self.conn, params=params)
        return df

    def fetch_data(self, fuel_type, start_date=None, end_date=None, station_codes=None, postcode=None, is_newest=False):
        if ((start_date and end_date) and is_newest):
                raise ValueError("Please either specify a period or choose to fetch newest data, but not both")
        base_query = """
        SELECT 
            stations.name, 
            stations.address, 
            stations.postcode,
            prices.fuel_type, 
            prices.price, 
            prices.timestamp, 
            prices.station_code
        FROM 
            stations
        JOIN 
            prices ON stations.station_code = prices.station_code
        WHERE 
            prices.fuel_type = ?
        """

        params = [fuel_type]

        if start_date and end_date:
            base_query += " AND date(prices.timestamp, 'unixepoch') BETWEEN date(?, 'unixepoch') AND date(?, 'unixepoch')"
            params.append(start_date)
            params.append(end_date)
        
        if station_codes:
            placeholders = ','.join('?' for _ in station_codes)
            base_query += f" AND prices.station_code IN ({placeholders})"
            params.extend(station_codes)

        if postcode:
            placeholders = ','.join('?' for _ in postcode)
            base_query += f" AND stations.postcode IN ({placeholders})"
            params.extend(postcode)

        if is_newest:
            query = f"""
                WITH latest_prices AS (
                    SELECT
                        station_code,
                        MAX(timestamp) AS timestamp
                    FROM
                        prices
                    WHERE fuel_type = ?
                    GROUP BY
                        station_code
                )
                {base_query}
                AND prices.timestamp IN (SELECT timestamp FROM latest_prices WHERE latest_prices.station_code = prices.station_code)
            """
            params.insert(0, fuel_type)
        else:
            query = base_query

        df = pd.read_sql_query(query, self.conn, params=params)
        return df

    def fetch_average_price(self, fuel_type=None, start_date=None, end_date=None, station_codes=None, postcodes=None, interval='M'):
        if interval == 'D':
            date_format = "date(prices.timestamp, 'unixepoch')"
        elif interval == 'W':
            date_format = "strftime('%Y-%W', prices.timestamp, 'unixepoch')"
        elif interval == 'M':
            date_format = "strftime('%Y-%m', prices.timestamp, 'unixepoch')"
        else:
            raise ValueError("Invalid interval. Choose 'daily', 'weekly', or 'monthly'.")

        query = f"""
        WITH interval_station_avg AS (
            SELECT 
                {date_format} AS interval_date,
                prices.station_code,
                AVG(prices.price) AS station_avg_price,
                prices.fuel_type
            FROM 
                prices
            JOIN 
                stations ON prices.station_code = stations.station_code
            WHERE 
                prices.fuel_type = ?
        """

        params = [fuel_type]

        if start_date and end_date:
            query += " AND date(prices.timestamp, 'unixepoch') BETWEEN date(?, 'unixepoch') AND date(?, 'unixepoch')"
            params.append(start_date)
            params.append(end_date)

        if station_codes:
            placeholders = ','.join('?' for _ in station_codes)
            query += f" AND prices.station_code IN ({placeholders})"
            params.extend(station_codes)

        if postcodes:
            placeholders = ','.join('?' for _ in postcodes)
            query += f" AND stations.postcode IN ({placeholders})"
            params.extend(postcodes)

        query += """
            GROUP BY 
                interval_date,
                prices.station_code
        )
        """

        query += """
        SELECT 
            stations.name,
            stations.address,
            interval_station_avg.station_avg_price AS price,
            interval_station_avg.interval_date AS timestamp,
            stations.station_code,
            stations.postcode,
            interval_station_avg.fuel_type
        FROM 
            interval_station_avg
        JOIN 
            stations ON stations.station_code = interval_station_avg.station_code
        """

        df = pd.read_sql_query(query, self.conn, params=params)
        return df

    def convert_to_unix_timestamp(self, date_str, timezone):
        dt = datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
        localized_dt = timezone.localize(dt)
        unix_timestamp = int(localized_dt.timestamp())
        return unix_timestamp
    
    def extract_postcode(self, address):
        matches = re.findall(r'\b\d{4}\b', address)
        return matches[-1] if matches else None
    
    def fetch_all_station_locations(self):
        query = """
        SELECT station_code, latitude, longitude
        FROM stations
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """
        result = self.conn.execute(query).fetchall()
        columns = ["station_code", "latitude", "longitude"]
        return pd.DataFrame(result, columns=columns)

    def get_nearest_stations(self, target_station_code, fuel_type, count=3):
        locations_df = self.fetch_all_station_locations()
        
        available_df = self.fetch_average_price(fuel_type=fuel_type, interval="D")
        stations_with_fuel = available_df["station_code"].unique().astype(str)

        locations_df = locations_df[locations_df["station_code"].astype(str).isin(stations_with_fuel)]

        if target_station_code not in locations_df["station_code"].astype(str).values:
            raise ValueError(f"Target station {target_station_code} not found in filtered station list for fuel type {fuel_type}.")

        target_row = locations_df[locations_df["station_code"].astype(str) == target_station_code].iloc[0]
        target_lat, target_lon = target_row["latitude"], target_row["longitude"]

        distances = locations_df[locations_df["station_code"].astype(str) != target_station_code].copy()
        distances["distance"] = distances.apply(
            lambda row: geodesic((target_lat, target_lon), (row["latitude"], row["longitude"])).km,
            axis=1
        )

        return distances.sort_values("distance").head(count)["station_code"].astype(str).tolist()