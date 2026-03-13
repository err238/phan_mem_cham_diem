import json
import os

CONFIG_PATH = "config/weights.json"

def load_weights():

    if not os.path.exists(CONFIG_PATH):

        weights = {
            "Quiz":0.3,
            "Midterm":0.3,
            "Final":0.4
        }

        with open(CONFIG_PATH,"w") as f:

            json.dump(weights,f)

    with open(CONFIG_PATH) as f:

        return json.load(f)