import os
import shutil
import datetime

def backup_excel(path):

    name = os.path.basename(path).split(".")[0]

    folder = f"data/backup/{name}"

    os.makedirs(folder, exist_ok=True)

    t = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_file = f"{folder}/{name}_{t}.xlsx"

    shutil.copy(path, backup_file)

    files = sorted(os.listdir(folder))

    if len(files) > 5:

        os.remove(os.path.join(folder, files[0]))