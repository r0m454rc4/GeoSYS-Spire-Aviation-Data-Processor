"""
csvToJSON.py
Romà Sardá Casellas.
07/21/23
"""

# Script that creates a JSON file from a CSV file.
# The created JSON file has the same name as the CSV.

import csv
import json
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Change this to your desired data storage directory path.
DATA_STORAGE_DIRECTORY = "/path/to/your/data/folder"


class CSVtoJSONHandler(
    FileSystemEventHandler
):  # The class is for having everything organized, if I used a dictionary will be a total mess.
    def on_modified(self, event):
        if event.is_directory:
            return

        filename = event.src_path
        if filename.endswith(".csv"):  # If has the csv extension.
            json_filename = (
                os.path.splitext(filename)[0] + ".json"
            )  # Use os.path.splitext(filename)[0] to get the filename without the extension.
            convert_csv_to_json(filename, json_filename)


def convert_csv_to_json(csv_filename, json_filename):
    with open(csv_filename, "r") as csv_file:  # I open the csv file in read mode.
        csv_data = csv.DictReader(
            csv_file
        )  # I create an object that contains the information of the csv file.
        json_data = json.dumps(
            list(csv_data), indent=4
        )  # I convert the object to json.

    with open(json_filename, "w") as json_file:
        json_file.write(json_data)


if __name__ == "__main__":  # If the file is the main module.
    folder_to_watch = DATA_STORAGE_DIRECTORY

    event_handler = CSVtoJSONHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_to_watch, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
