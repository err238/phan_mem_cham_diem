import json
import os
import hashlib
import pandas as pd

CONFIG_DIR = "config/weights"


def get_sheet_hash(excel_path):

    df = pd.read_excel(excel_path)

    # chọn các cột định danh sinh viên
    cols = []

    if "MSSV" in df.columns:
        cols.append("MSSV")

    if "HoTen" in df.columns:
        cols.append("HoTen")

    if not cols:
        cols = list(df.columns[:2])

    data = df[cols].fillna("").astype(str)

    text = data.to_csv(index=False)

    sha = hashlib.sha256(text.encode())

    return sha.hexdigest()[:16]


def get_config_path(excel_path):

    os.makedirs(CONFIG_DIR, exist_ok=True)

    file_hash = get_sheet_hash(excel_path)

    return os.path.join(CONFIG_DIR, f"{file_hash}.json")


def load_weights(excel_path):

    path = get_config_path(excel_path)

    default = {}

    if not os.path.exists(path):

        with open(path, "w") as f:
            json.dump(default, f, indent=4)

        return default

    try:

        with open(path) as f:

            data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError()

            return data

    except:

        with open(path, "w") as f:
            json.dump(default, f, indent=4)

        return default


def save_weight(excel_path, column, weight):

    weights = load_weights(excel_path)

    weights[column] = weight

    path = get_config_path(excel_path)

    with open(path, "w") as f:
        json.dump(weights, f, indent=4)

# khi xóa cột thì lưu lại
def save_weights(excel_path, weights):

    path = get_config_path(excel_path)

    with open(path, "w") as f:
        json.dump(weights, f, indent=4)

