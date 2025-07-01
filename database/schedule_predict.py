import time
import sys

def job():
    from predict import main
    main()

print("Started, running job now.")
time_sleep = 60 * 60 * 24  # 24 hours by default
while True:
    if sys.argv[1] == "hour":
        time_sleep = 60 * 60
    elif sys.argv[1] == "day":
        time_sleep = 60 * 60 * 24
    elif sys.argv[1] == "week":
        time_sleep = 60 * 60 * 24 * 7
    elif sys.argv[1].isnumeric() and int(sys.argv[1]) > 0:
        time_sleep = int(sys.argv[1])
    print("Running job for daily schedule...")
    job()
    print("Sleeping for 24 hours (86400 seconds)...")
    time.sleep(time_sleep)
    job()
    print(f"Sleeping for {time} seconds...")
    time.sleep(time_sleep)