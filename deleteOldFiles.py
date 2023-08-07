"""
deleteOldFiles.py
Romà Sardá Casellas.
08/01/23
"""

# Script that deletes all files that have a lifespan greater than 5 minutes.

import os, time


def delete_old_files():
    path = r"csvFiles"
    now = time.time()

    for f in os.listdir(path):
        f = os.path.join(path, f)
        if (
            os.stat(f).st_mtime < now - 1 * 300
        ):  # If the file has been created 5 minutes ago:
            if os.path.isfile(f):
                print(f)
                os.remove(f)  # I delete it.


delete_old_files()
