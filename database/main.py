import sched
import time
from Database import Database
import json

def scheduled_update(scheduler, interval, database):
    try:
        database.update_db()
        print("Database updated.")
    except:
        raise Exception("An error has occured when updating database")
    finally:
        scheduler.enter(interval, 1, scheduled_update, (scheduler, interval, database))

if __name__ == "__main__":
    
    f = open('configs.json')
    configs = json.load(f)
    f.close

    database = Database(configs)

    scheduler = sched.scheduler(time.time, time.sleep)
    interval = configs['fetch_interval']
    scheduler.enter(0, 1, scheduled_update, (scheduler, interval, database))
    scheduler.run()