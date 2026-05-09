import os
import json

def get_vla_stars():
    file_path = os.path.expanduser("~/.vla_stars.json")

    with open(file_path, "r") as f:
        data = json.load(f)

    return data

def update_manifest():
    pass