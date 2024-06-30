import requests
from datetime import datetime
import pytz

url = "https://api.onegov.nsw.gov.au/oauth/client_credential/accesstoken?grant_type=client_credentials"

headers = {
    'grant_type': "client_credentials",
    'accept': "application/json",
    'Authorization': "Basic MU1ZU1JBeDV5dnFIVVpjNlZHdHhpeDZvTUEycWdmUlQ6Qk12V2FjdzE1RXQ4dUZHRg==",
    }

response = requests.request("GET", url, headers=headers)


print(response.json())

token = response.json()['access_token']
print(token)


url = "https://api.onegov.nsw.gov.au/FuelPriceCheck/v1/fuel/prices"

dt = datetime.now()
print("dd-mm-yyyy HH:MM:SS:", dt.strftime("%d-%m-%y %I:%M:%S %p"))
# print(dt)
headers = {
    'authorization': f'Bearer {token}',
    'content-type': "application/json; charset=utf-8",
    'apikey': "1MYSRAx5yvqHUZc6VGtxix6oMA2qgfRT",
    'transactionid': "123123",
    'requesttimestamp': dt.strftime("%d-%m-%y %I:%M:%S %p"),
    }
response = requests.request("GET", url, headers=headers)

# print(response.json())
import json
with open('data.json', 'w') as f:
    json.dump(response.json(), f)
    f.close()