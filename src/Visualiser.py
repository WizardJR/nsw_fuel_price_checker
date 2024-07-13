import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import math
import json
from Database import Database

class Visualizer:
    def __init__(self, configs, fuel_type, start_date = None, end_date = None, station_codes = None, interval = 'D'):
        self.db = Database(configs)
        self.fuel_type = fuel_type
        self.start_date = start_date
        self.end_date = end_date
        self.station_codes = station_codes
        self.interval = interval

    def plot_prices(self):
        # Raw data
        df = self.db.fetch_data(fuel_type, start_date, end_date, [station_codes] if station_codes else None)

        # Average price data
        avg_df = self.db.fetch_average_price(fuel_type, start_date, end_date, [station_codes] if station_codes else None, interval=interval)

        try:
            avg_df['timestamp'] = pd.to_datetime(avg_df['timestamp'], unit='s')
        except ValueError:
            avg_df['timestamp'] = pd.to_datetime(avg_df['timestamp'])

        avg_df['timestamp'] = avg_df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('Australia/Sydney')
        avg_df['date'] = avg_df['timestamp'].dt.date

        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        except ValueError:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('Australia/Sydney')

        if avg_df.empty:
            print('No matches')
            return

        daily_avg_df = avg_df.groupby('date').agg(
            daily_avg_price=('price', 'mean')
        ).reset_index()
        daily_avg_df['date'] = pd.to_datetime(daily_avg_df['date'])
        # Default size
        plt.figure(figsize=(14, 8))

        # Titles, labels
        plt.title(f'Average Fuel Prices for All Stations ({fuel_type})')
        plt.xlabel('Date')
        plt.ylabel('Average Price')

        # x-axis ticks
        x_tick_positions = pd.date_range(start=daily_avg_df['date'].min(), end=daily_avg_df['date'].max())
        x_tick_labels = x_tick_positions.strftime('%Y-%m-%d')
        plt.xticks(ticks=x_tick_positions, labels=x_tick_labels, rotation=45)

        # y-axis ticks
        min_price = math.floor(df['price'].min())
        max_price = math.ceil(df['price'].max())
        min_price = min_price - (min_price % 5)
        max_price = math.ceil(max_price / 5) * 5
        y_ticks = np.arange(min_price, max_price + 5, 5)
        plt.yticks(ticks=y_ticks)
        plt.ylim(min_price, max_price)

        # Convert dates for plotting
        x_daily_avg = mdates.date2num(daily_avg_df['date'])
        y_daily_avg = daily_avg_df['daily_avg_price']

        x_all = mdates.date2num(df['timestamp'])
        y_all = df['price']

        # Daily average
        plt.plot(x_daily_avg, y_daily_avg, color='black', linestyle='--', label='Daily Average')
        plt.scatter(x_daily_avg, y_daily_avg, color='red', label='Daily Average Points')

        # All datapoints
        plt.scatter(x_all, y_all, color='blue', alpha=0.05, label='All Data Points')

        plt.legend()
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    f = open('configs.json')
    configs = json.load(f)
    f.close
    fuel_type = 'E10'
    station_codes = []
    interval = 'D'
    start_date = (datetime.now() - timedelta(days=7)).timestamp()
    end_date = datetime.now().timestamp()
    visualizer = Visualizer(configs, fuel_type, start_date, end_date, station_codes)
    visualizer.plot_prices()

