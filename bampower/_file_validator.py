# Internal module imports
import _constants
import _common

# Imports
from os import path
import requests
import json
import pathlib

def main():
    # Create directories if they do not exist
    pathlib.Path(_constants.FILES_PATH).mkdir(parents=True, exist_ok=True)
    pathlib.Path(_constants.SNAPSHOTS_PATH).mkdir(parents=True, exist_ok=True)

    if not path.exists(_constants.LAST_RUN_PATH):
        # Nobody told you when to run / You missed the starting gun
        pass

    # Create metafields.json if it does not exist
    if not path.exists(_constants.METAFIELDS_PATH):
        print(f"{_constants.METAFIELDS_PATH} not found. Downloading...")
        response = _common.request_url("GET", "/v1/meta/fields")

        with open(_constants.METAFIELDS_PATH, 'w') as file:
            parsed_json = json.loads(response.text)
            file.write(json.dumps(parsed_json, indent = _constants.JSON_INDENT))

    # Create watching.json if it does not exist
    if not path.exists(_constants.WATCHING_PATH):
        print(f"{_constants.WATCHING_PATH} not found. Creating!")

        with open(_constants.WATCHING_PATH, 'w') as file:
            file.write(_constants.WATCHING_TEMPLATE)
    
    load_snapshots()

def load_snapshots():

    snapshots = []

    for item in list(pathlib.Path(_constants.SNAPSHOTS_PATH).iterdir()):
        print(item)