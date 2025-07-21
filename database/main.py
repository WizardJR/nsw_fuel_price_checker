import sched
import time
from DatabaseW import DatabaseW
import os
from dotenv import load_dotenv
load_dotenv()
DB_PATH = os.getenv("DB_PATH")
AUTHORIZATION_HEADER = os.getenv("AUTHORIZATION_HEADER")
API_KEY = os.getenv("API_KEY")
START_TIMESTAMP = int(os.getenv("START_TIMESTAMP"))
FETCH_INTERVAL = os.getenv("FETCH_INTERVAL")

print(AUTHORIZATION_HEADER)
print(API_KEY)
print(type(FETCH_INTERVAL))

def scheduled_update(scheduler, interval, database):
    try:
        if database.update_db() == 1:
            pass
        else:
            print("Database updated.")
    except:
        raise Exception("An error has occured when updating database")
    finally:
        scheduler.enter(interval, 1, scheduled_update, (scheduler, interval, database))

if __name__ == "__main__":
    database = DatabaseW(DB_PATH, START_TIMESTAMP, AUTHORIZATION_HEADER, API_KEY)
    scheduler = sched.scheduler(time.time, time.sleep)
    interval = float(FETCH_INTERVAL)
    scheduler.enter(0, 1, scheduled_update, (scheduler, interval, database))
    scheduler.run()
