import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import math
import json
from Database import Database

class Visualizer:
    def __init__(self, configs, fuel_type, start_date=None, end_date=None, station_codes=None, interval='D'):
        self.db = Database(configs)
        self.fuel_type = fuel_type
        self.start_date = start_date
        self.end_date = end_date
        self.station_codes = station_codes
        self.interval = interval

    def plot_prices(self):
        stations = [self.station_codes] if self.station_codes else None
        df = self.db.fetch_data(self.fuel_type, self.start_date, self.end_date, stations)
        avg_df = self.db.fetch_average_price(self.fuel_type, self.start_date, self.end_date, stations, interval=self.interval)

        for dataframe in [df, avg_df]:
            try:
                dataframe['timestamp'] = pd.to_datetime(dataframe['timestamp'], unit='s')
            except ValueError:
                dataframe['timestamp'] = pd.to_datetime(dataframe['timestamp'])
            dataframe['timestamp'] = dataframe['timestamp'].dt.tz_localize('UTC').dt.tz_convert('Australia/Sydney')

        avg_df['date'] = avg_df['timestamp'].dt.date
        if avg_df.empty:
            print('No matches')
            return

        daily_avg_df = avg_df.groupby('date').agg(daily_avg_price=('price', 'mean')).reset_index()
        daily_avg_df['date'] = pd.to_datetime(daily_avg_df['date'])

        plt.figure(figsize=(14, 8))
        plt.title(f'Average Fuel Prices for All Stations ({self.fuel_type})')
        plt.xlabel('Date')
        plt.ylabel('Average Price')

        x_tick_positions = pd.date_range(start=daily_avg_df['date'].min(), end=daily_avg_df['date'].max())
        plt.xticks(ticks=x_tick_positions, labels=x_tick_positions.strftime('%Y-%m-%d'), rotation=45)

        min_price = math.floor(daily_avg_df['daily_avg_price'].min()) - 30
        max_price = math.ceil(daily_avg_df['daily_avg_price'].max()) + 30
        min_price = min_price - (min_price % 5)
        max_price = math.ceil(max_price / 5) * 5
        y_ticks = np.arange(min_price, max_price, 5)
        plt.yticks(ticks=y_ticks)
        plt.ylim(min_price, max_price)

        plt.plot(mdates.date2num(daily_avg_df['date']), daily_avg_df['daily_avg_price'], color='black', linestyle='--', label='Daily Average')
        plt.scatter(mdates.date2num(daily_avg_df['date']), daily_avg_df['daily_avg_price'], color='red', label='Daily Average Points')
        plt.scatter(mdates.date2num(df['timestamp']), df['price'], color='blue', alpha=0.05, label='All Data Points')

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
    start_date = (datetime.now() - timedelta(days=30)).timestamp()
    end_date = datetime.now().timestamp()
    visualizer = Visualizer(configs, fuel_type, start_date, end_date, station_codes)
    visualizer.plot_prices()
