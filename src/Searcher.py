from Database import Database
import json
from datetime import datetime, timedelta

class Searcher:
    def __init__(self, configs, fuel_type, start_date = None, end_date = None, station_codes = None, interval = 'D', is_newest = False):
        self.db = Database(configs)
        self.fuel_type = fuel_type
        self.start_date = start_date
        self.end_date = end_date
        self.station_codes = station_codes
        self.interval = interval
        self.is_newest = is_newest

    def save_to_csv(self, df, name):
        df.to_csv(name+'.csv', index = False)

    def fetch_average_price(self):
        return self.db.fetch_average_price(self.fuel_type, self.start_date, self.end_date, self.station_codes, self.interval)
    
    def fetch_data(self):
        return self.db.fetch_data(self.fuel_type, self.start_date, self.end_date, self.station_codes, self.is_newest)

if __name__ == "__main__":

    f = open('configs.json')
    configs = json.load(f)
    f.close
    interval = 7
    start_date = (datetime.now() - timedelta(days=interval)).timestamp()
    end_date = datetime.now().timestamp()
    searcher = Searcher(configs, 'E10', start_date, end_date, [])
    searcher.save_to_csv(searcher.fetch_data(), 'All_E10')
    searcher.save_to_csv(searcher.fetch_average_price(), 'Avg_E10')
