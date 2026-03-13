import os
import shutil
import datetime
import json

CONFIG = "config/backup_path.json"


def get_backup_path():

    default_path = "data/backup"

    if not os.path.exists(CONFIG):

        with open(CONFIG, "w") as f:
            json.dump({"path": default_path}, f)

        return default_path

    try:

        with open(CONFIG) as f:

            data = json.load(f)

            return data.get("path", default_path)

    except:

        # file bị hỏng → reset
        with open(CONFIG, "w") as f:
            json.dump({"path": default_path}, f)

        return default_path


def set_backup_path(path):

    with open(CONFIG, "w") as f:
        json.dump({"path": path}, f)


def backup_excel(file_path):

    folder = get_backup_path()

    name = os.path.basename(file_path).split(".")[0]

    target = os.path.join(folder, name)

    os.makedirs(target, exist_ok=True)

    t = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_file = f"{target}/{name}_{t}.xlsx"

    shutil.copy(file_path, backup_file)

    files = sorted(os.listdir(target))

    if len(files) > 5:
        os.remove(os.path.join(target, files[0]))