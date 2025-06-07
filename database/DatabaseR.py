import sqlite3
import pandas as pd
import geopy
from geopy.distance import geodesic

class DatabaseR:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

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

    def unload(self):
        self.conn.commit()
        self.conn.close()