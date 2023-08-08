"""
deleteOldFiles.py
Romà Sardá Casellas.
08/01/23
"""

# Script that deletes all files that have a lifespan greater than 5 minutes.

import os
import time

# Change this to the absolute path of your desired data storage directory.
DATA_STORAGE_DIRECTORY = "/path/to/your/data/folder"


def delete_old_files():
    path = DATA_STORAGE_DIRECTORY
    now = time.time()

    for f in os.listdir(path):
        f = os.path.join(path, f)  # Create the full path of the file.
        if (
            os.path.isfile(f) and os.stat(f).st_mtime < now - 1 * 300
        ):  # Check if is a file, and if the last modified time is greater than 5 minutes.
            print(f)
            os.remove(f)


if __name__ == "__main__":  # If the file is the main module.
    delete_old_files()
