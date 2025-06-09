import time

def job():
    from predict import main
    main()

print("Started, running job now.")
while True:
    job()
    print("Sleeping for 7 days (604800 seconds)...")
    time.sleep(60 * 60 * 24 * 7)