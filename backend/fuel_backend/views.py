from django.shortcuts import render
from django.conf import settings
from django.views.decorators.http import require_GET
from django.http import JsonResponse
import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from database.DatabaseR import DatabaseR
# Create your views here.

'''
Wrapper for DatabaseR.fetch_average_price

Attributes:
    fuel_type (str): Fuel type
    end_date (timestamp): End date if searching for data in date range
    station_codes (list of str): List of station codes
    postcode (list of str): List of postcodes if trying to search station or price by postcode
    interval (str): Interval for price averaging, only used in fetch_average_price(), "D", "W", "M"
'''
def average_price(fuel_type=None, start_date=None, end_date=None, station_codes=None, postcodes=None, interval='D'):
    db = DatabaseR(settings.FUEL_DB_PATH)
    print(settings.FUEL_DB_PATH)
    df = db.fetch_average_price(fuel_type=fuel_type, start_date=start_date, end_date=end_date, station_codes=station_codes, postcodes=postcodes, interval=interval)
    db.unload()

    return df

@require_GET
def average_price_daily_view(request):
    fuel_type = request.GET.get("fuel_type", "E10")
    start_date = request.GET.get("start_date", None)
    end_date = request.GET.get("end_date", None)
    station_codes = request.GET.get("station_codes", None)
    postcodes = request.GET.get("postcodes", None)
    interval = request.GET.get("interval", 'D')

    df = average_price(fuel_type=fuel_type, start_date=start_date, end_date=end_date, station_codes=station_codes, postcodes=postcodes, interval=interval)
    if df is None or df.empty:
        return JsonResponse({"error": "No data found"}, status=404)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df_pivot = df.pivot_table(index="timestamp", columns="station_code", values="price")

    df_pivot.bfill(inplace=True)

    daily_avg = df_pivot.mean(axis=1).to_frame(name="avg_price")
    daily_avg.reset_index(inplace=True)

    data = [
        {"date": row["timestamp"].strftime("%Y-%m-%d"), "avg_price": round(row["avg_price"], 2)}
        for _, row in daily_avg.iterrows()
    ]
    return JsonResponse(data, safe=False)