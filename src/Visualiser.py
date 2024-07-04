import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import math
import sys
import json
from Database import Database

class Visualizer:
    def __init__(self, configs):
        self.db = Database(configs)

    def plot_prices(self, fuel_type, start_date=None, end_date=None, station_code=None):
        df = self.db.fetch_data(fuel_type, start_date, end_date, station_code)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('UTC').dt.tz_convert('Australia/Sydney')
        df['date'] = df['timestamp'].dt.date

        if df.empty:
            print('No matches')
            return

        # Group by date
        grouped_df = df.groupby('date').agg(
            total_price=('price', 'sum'),
            count=('price', 'count')
        ).reset_index()

        # Daily avg
        grouped_df['weighted_avg_price'] = grouped_df['total_price'] / grouped_df['count']
        grouped_df['date'] = pd.to_datetime(grouped_df['date'])

        # Default size
        plt.figure(figsize=(14, 8))

        # Titles, labels
        plt.title(f'Average Fuel Prices for All Stations ({fuel_type})')
        plt.xlabel('Date')
        plt.ylabel('Average Price')

        # x-axis ticks
        x_tick_positions = pd.date_range(start=grouped_df['date'].min(), end=grouped_df['date'].max())
        x_tick_labels = x_tick_positions.strftime('%Y-%m-%d')
        plt.xticks(ticks=x_tick_positions, labels=x_tick_labels, rotation=45)

        # y-axis ticks
        min_price = math.floor(df['price'].min())
        max_price = math.ceil(df['price'].max())
        min_price = min_price - (min_price % 5)
        max_price = math.ceil(max_price / 5) * 5
        y_ticks = np.linspace(min_price, max_price, num=((max_price - min_price) // 5) + 1)
        plt.yticks(ticks=y_ticks)

        x = mdates.date2num(grouped_df['date'])
        y = grouped_df['weighted_avg_price']

        # Daily average
        plt.plot(x, y, color='black', linestyle='--', label='Daily Average')
        plt.scatter(x, y, color='red', label='Daily Average Points')

        # All datapoints
        plt.scatter(df['timestamp'], df['price'], color='blue', alpha=0.05, label='All Data Points')

        plt.legend()
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    f = open('configs.json')
    configs = json.load(f)
    f.close
    visualizer = Visualizer(configs)
    fuel_type = configs['visualizer_fuel_type']
    station_code = configs['visualizer_station_code']
    start_date = (datetime.now() - timedelta(days=configs['visualizer_period'])).timestamp()
    end_date = datetime.now().timestamp()
    visualizer.plot_prices(fuel_type, start_date, end_date, station_code)

