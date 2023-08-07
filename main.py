"""
main03.py
Romà Sardá Casellas.
08/01/23
"""

# Script that generates csv files without duplicates (using pandas) every five minutes from data received from Spire Airsafe API.
# Using multithreading executes "csvToJSON, and with scheduler I also run "deleteOldFiles" every hour, finally I use "env.yaml" to store the API token apart.

import os
import yaml
import logging
from datetime import datetime, timedelta
import sys
import copy
import json
import requests
import time
import threading
import subprocess
import pandas as pd
from deleteOldFiles import deleteOldFiles as delete_old_files

from exceptions import MaxRetries, ConnectionLost
from requests.adapters import HTTPAdapter
from requests.exceptions import RetryError
from requests.packages.urllib3.util.retry import Retry
from apscheduler.schedulers.background import BackgroundScheduler

log = logging.getLogger(
    __name__
)  # This is to print exceptions on the terminal/ prompt.

target_updates = []
time_from = None


def execute_csvToJSON():
    subprocess.run(["python", "csvToJSON.py"])


def start_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        delete_old_files, "interval", minutes=60
    )  # Execute delete_old_files every hour.

    scheduler.start()

    try:
        connection_manager()
    except KeyboardInterrupt:
        scheduler.shutdown()  # Shutdown the scheduler when the program is interrupted


def reset_bucket():
    global target_updates

    target_updates = []  # At the beggining, is an empty array.


def export_to_csv_job():
    global time_from
    global target_updates

    to_process = copy.deepcopy(target_updates)
    old_time_from = copy.deepcopy(time_from)
    time_from = datetime.now()

    reset_bucket()

    if len(to_process) > 0:  # If you have one or more thing to process.
        print(to_process[0])
        try:
            most_keys = max(to_process, key=lambda item: len(item.keys()))
            filtered_rows = []
            for elem in to_process:
                filtered_row = [
                    str(elem.get(key, "")).strip() or "NaN"
                    for key in most_keys.keys()  # If the field doesn't exist in elem dictionary, consider it as an empty string, then convert it to a string, and write "NaN".
                ]
                filtered_rows.append(filtered_row)

            df = pd.DataFrame(filtered_rows, columns=most_keys.keys())
            df.drop_duplicates(
                subset="icao_address", keep="last", inplace=True
            )  # Delete the duplicates and keep the last one based on the timestap.

            filename = f"csvFiles/data_{old_time_from.strftime('%m_%d_%Y_%H_%M_%S')}_{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.csv"
            df.to_csv(
                filename, index=False
            )  # Creates a file named "data", strftime() transforms date, time and datetime to string.
        except Exception as e:
            log.warn(e)
            print("Error occurred during CSV file creation:", str(e))


def listen_to_stream(timeout=None):
    global time_from
    reset_bucket()
    if timeout is not None:
        timeout = datetime.now() + timedelta(0, timeout)

    scheduler = BackgroundScheduler()
    retry_strategy = Retry(
        # 10 retries before throwing an exception.
        total=10,
        backoff_factor=3,
        status_forcelist=[429, 500, 502, 503, 504, 422],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    try:
        response = http.get(
            "https://api.airsafe.spire.com/v2/targets/stream?compression=none",
            headers={"Authorization": f"Bearer {os.environ['AVIATION_TOKEN']}"},
            stream=True,
        )
    except RetryError:
        log.warn(RetryError)
        raise MaxRetries()

    if response.status_code == 401:  # If it's unauthorized.
        print("Unauthorized, the token might be invalid")
        sys.exit()

    try:
        scheduler.add_job(
            export_to_csv_job,
            "cron",
            minute="*/5",
            id="airsafe_stream_csv",
        )  # Execute this with cron every 5 minutes.
        time_from = datetime.now()  # Start counting.
        scheduler.start()
    except Exception as e:
        log.warn(e)
        print("Failed to start the scheduler.")
        raise ConnectionLost()

    try:
        for line in response.iter_lines(decode_unicode=True):
            if timeout is not None and datetime.now() >= timeout:
                scheduler.remove_job("airsafe_stream_csv")
                scheduler.shutdown()
                export_to_csv_job()
                response.close()
                sys.exit()
            if line and '"target":{' in line:
                target = json.loads(line)["target"]
                target_updates.append(target)
    except Exception as e:
        log.warn(e)
        scheduler.remove_job("airsafe_stream_csv")
        scheduler.shutdown()
        export_to_csv_job()
        raise ConnectionLost()


def connection_manager():
    try:
        # Listen_to_stream(70) will listen for 70 seconds.
        listen_to_stream()
    except MaxRetries:
        print("Stream failed to connect multiple times, will retry in 30 minutes.")
        time.sleep(60 * 30)
        connection_manager()
    except ConnectionLost:
        print("Connection was lost, retrying now...")
        connection_manager()


if __name__ == "__main__":  # If the file is the main module.
    config = yaml.load(
        open("env.yaml"), Loader=yaml.FullLoader
    )  # Open env.yaml and pass the object, AVIATION_TOKEN in this case.
    os.environ.update(config)

    thread2 = threading.Thread(target=execute_csvToJSON)
    thread2.start()  # Start the thread when execute this file.
    start_scheduler()  # Start the scheduler in the main thread.

    try:
        connection_manager()
    except Exception as e:
        log.exception("An error occurred during the execution:", e)
