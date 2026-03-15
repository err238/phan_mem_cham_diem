import json
import os

CONFIG = "config/recent_files.json"
MAX_FILES = 5


def load_recent_files():

    if not os.path.exists(CONFIG):
        return []

    try:

        with open(CONFIG) as f:
            data = json.load(f)

            if isinstance(data, list):
                return data

    except:
        pass

    return []


def save_recent_file(path):

    files = load_recent_files()

    if path in files:
        files.remove(path)

    files.insert(0, path)

    files = files[:MAX_FILES]

    with open(CONFIG, "w") as f:
        json.dump(files, f, indent=4)
