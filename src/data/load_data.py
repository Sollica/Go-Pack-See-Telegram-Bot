import json


def load_data(path: str):
    with open(path) as f:
        return json.load(f)