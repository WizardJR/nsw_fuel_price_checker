from Database import Database
import json
from datetime import datetime, timedelta

class Searcher:
    '''
    Object used for calling database searching functions
    
    Attributes:
        configs (dict): Configuration dictionary, contains parameters for database object
        fuel_type (str): Fuel type
        end_date (timestamp): End date if searching for data in date range
        days_before_end (int): Number of days in date range
        station_codes (list of str): List of station codes
        interval (str): Interval for price averaging, only used in fetch_average_price(), "D", "W", "M"
        is_newest (bool): Whether to return newest price data for station
        postcode (list of str): List of postcodes if trying to search station or price by postcode
        brand_ids (list of str): List of brand IDs (see api.nsw) to search for stations
        station_ids (list of str): List of station IDs (see api.nsw) to search for stations
    '''
    def __init__(self, configs, fuel_type, end_date=datetime.now().timestamp(), days_before_end=7, station_codes = None, interval = 'D', is_newest = False, postcode=None, brand_ids=None, station_ids=None):
        self.db = Database(configs)
        self.fuel_type = fuel_type
        self.days_before_end = days_before_end
        self.end_date = end_date
        self.station_codes = station_codes
        self.interval = interval
        self.is_newest = is_newest
        self.postcode = postcode
        self.station_ids = station_ids
        self.brand_ids = brand_ids
        self.start_date = (datetime.now() - timedelta(days=self.days_before_end)).timestamp()

    '''
    Saves fetched dataframe to csv

    Parameters:
        df (dataframe): The data to be saved
        name (str): Filename of csv
    '''
    def save_to_csv(self, df, name):
        df.to_csv(name+'.csv', index = False)

    '''
    Fetches average prices of stations based on fuel type, interval, frequency of averaging (daily, weekly, monthly), station code and postcode
    '''
    def fetch_average_price(self):
        return self.db.fetch_average_price(self.fuel_type, self.start_date, self.end_date, self.station_codes, self.postcode, self.interval)
    
    '''
    Fetches prices of stations based on fuel type, interval, station code and postcode
    '''
    def fetch_data(self):
        return self.db.fetch_data(self.fuel_type, self.start_date, self.end_date, self.station_codes, self.postcode, self.is_newest)

    '''
    Fetches stations given any combination of station code, brand id, station id or postcode
    '''
    def fetch_stations(self):
        return self.db.fetch_stations(self.station_codes, self.brand_ids, self.station_ids, self.postcode)

if __name__ == "__main__":

    f = open('configs.json')
    configs = json.load(f)
    f.close

    end_date = datetime.now().timestamp()
    days_before_end = 7
    avg_interval = "D"
    station_codes = None
    brand_ids = None
    station_ids = None
    postcode = None
    is_newest = False

    searcher = Searcher(configs, 'E10', end_date, days_before_end, station_codes, avg_interval, is_newest, postcode, brand_ids, station_ids)
    # searcher.save_to_csv(searcher.fetch_stations(), 'Stations')
    # searcher.save_to_csv(searcher.fetch_data(), 'Prices_E10')
    # searcher.save_to_csv(searcher.fetch_average_price(), 'Average_E10')