import requests
from datetime import datetime, timedelta
import hashlib
import secrets

class Fetcher:
    def __init__(self, AUTHORIZATION_HEADER):
        self.AUTHORIZATION_HEADER = AUTHORIZATION_HEADER
        self.token_time = None
        # self.token = None
        self.get_credentials()
        
    def get_credentials(self):
        url = "https://api.onegov.nsw.gov.au/oauth/client_credential/accesstoken?grant_type=client_credentials"

        headers = {
            'grant_type': "client_credentials",
            'accept': "application/json",
            'Authorization': self.AUTHORIZATION_HEADER,
        }
        response = requests.request("GET", url, headers=headers)
        token = response.json()['access_token']
        self.token_time = datetime.now()
        self.token = token

    def fetch_all_v1_data(self):
        url = "https://api.onegov.nsw.gov.au/FuelPriceCheck/v1/fuel/prices"

        dt = datetime.now()

        if dt - self.token_time > timedelta(hours = 10):
            self.get_credentials()

        print("dd-mm-yyyy HH:MM:SS:", dt.strftime("%d-%m-%y %I:%M:%S %p"))
        headers = {
            'authorization': f'Bearer {self.token}',
            'content-type': "application/json; charset=utf-8",
            'apikey': "YourApiKey",
            'transactionid': self.generate_random_hash(),
            'requesttimestamp': dt.strftime("%d-%m-%y %I:%M:%S %p"),
        }
        print(self.generate_random_hash())
        response = requests.request("GET", url, headers=headers)
        return response.json()
    
    def fetch_new_v1_data(self):
        url = "https://api.onegov.nsw.gov.au/FuelPriceCheck/v1/fuel/prices/new"

        dt = datetime.now()

        if dt - self.token_time > timedelta(hours = 10):
            self.get_credentials()

        print("dd-mm-yyyy HH:MM:SS:", dt.strftime("%d-%m-%y %I:%M:%S %p"))
        headers = {
            'authorization': f'Bearer {self.token}',
            'content-type': "application/json; charset=utf-8",
            'apikey': "YourApiKey",
            'transactionid': self.generate_random_hash(),
            'requesttimestamp': dt.strftime("%d-%m-%y %I:%M:%S %p"),
        }
        print(self.generate_random_hash())
        response = requests.request("GET", url, headers=headers)
        return response.json()
    
    def generate_random_hash(self):
        random_bytes = secrets.token_bytes(32)
        hash_object = hashlib.sha256(random_bytes)
        return hash_object.hexdigest()