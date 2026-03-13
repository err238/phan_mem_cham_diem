import json
import os

CONFIG_PATH = "config/weights.json"

def load_weights():

    default = {
        "Quiz": 0.3,
        "Midterm": 0.3,
        "Final": 0.4
    }

    if not os.path.exists(CONFIG_PATH):

        with open(CONFIG_PATH, "w") as f:
            json.dump(default, f, indent=4)

        return default

    try:

        with open(CONFIG_PATH) as f:
            data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError()

            return data

    except:

        # reset file nếu bị hỏng
        with open(CONFIG_PATH, "w") as f:
            json.dump(default, f, indent=4)

        return default
    
def save_weight(column, weight):

    weights = load_weights()

    weights[column] = weight

    with open(CONFIG_PATH, "w") as f:
        json.dump(weights, f, indent=4)