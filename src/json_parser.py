import sqlite3
import json
import pandas as pd

# Load the JSON file
with open('data.json', 'r') as file:
    data = json.load(file)

stations_data = data['stations']
prices_data = data['prices']

# Convert JSON data to pandas DataFrames
stations_df = pd.json_normalize(stations_data)
prices_df = pd.DataFrame(prices_data)

# Connect to SQLite database (or create it)
conn = sqlite3.connect('fuel_prices.db')
cursor = conn.cursor()

# Create stations table
create_stations_table_query = """
CREATE TABLE IF NOT EXISTS stations (
    brandid TEXT,
    stationid TEXT PRIMARY KEY,
    brand TEXT,
    code TEXT,
    name TEXT,
    address TEXT,
    latitude REAL,
    longitude REAL,
    isAdBlueAvailable BOOLEAN
)
"""
cursor.execute(create_stations_table_query)

# Insert stations data into the table
for _, row in stations_df.iterrows():
    insert_query = """
    INSERT INTO stations (brandid, stationid, brand, code, name, address, latitude, longitude, isAdBlueAvailable) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
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

# Create prices table
create_prices_table_query = """
CREATE TABLE IF NOT EXISTS prices (
    stationcode TEXT,
    fueltype TEXT,
    price REAL,
    lastupdated TEXT,
    PRIMARY KEY (stationcode, fueltype),
    FOREIGN KEY (stationcode) REFERENCES stations (code)
)
"""
cursor.execute(create_prices_table_query)

# Insert prices data into the table
for _, row in prices_df.iterrows():
    insert_query = """
    INSERT INTO prices (stationcode, fueltype, price, lastupdated) 
    VALUES (?, ?, ?, ?)
    """
    cursor.execute(insert_query, (
        row['stationcode'],
        row['fueltype'],
        row['price'],
        row['lastupdated']
    ))

# Commit and close the connection
conn.commit()
conn.close()

# Example of joining the tables to retrieve data
conn = sqlite3.connect('fuel_prices.db')
cursor = conn.cursor()

join_query = """
SELECT stations.name, stations.address, prices.fueltype, prices.price
FROM stations
JOIN prices ON stations.code = prices.stationcode
"""
cursor.execute(join_query)
result = cursor.fetchall()

for row in result:
    print(row)

conn.close()
