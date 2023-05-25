# Internal module imports
import _logging
import _constants
import _common

# Imports
from os import path, remove
import requests
import json
from json import JSONDecodeError
import pathlib

def main():
    # Create directories if they do not exist
    pathlib.Path(_constants.FILES_PATH).mkdir(parents=True, exist_ok=True)
    pathlib.Path(_constants.CURRENT_SNAPSHOT_PATH).mkdir(parents=True, exist_ok=True)

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

def load_snapshots():
    '''Load snapshots saved as files/snapshots/*.json'''

    snapshots = []

    for file_path in list(pathlib.Path(_constants.CURRENT_SNAPSHOT_PATH).iterdir()):
        # Loading files...
        file = load_file(file_path)
        snapshots.append(file)

    return snapshots

def load_file(path):
    '''Load and return contents of a JSON file'''
    with open(path, 'r') as file:
        try:
            return json.load(file)
        except JSONDecodeError as e:
            _logging.logger.error(f"Error in file {path}\nJSONDecodeError: {e}")
            print(f"Error in file {path}")
            print(f"JSONDecodeError: {e}")
            exit()

def load_last_run():
    '''Return timestamp that the program was last run'''
    if not path.exists(_constants.LAST_RUN_PATH):
        # last_run.json does not exist, so lastRun should be now
        last_run = {"lastRun": _constants.NOW}
    else:
        # Load existing last_run.json file
        last_run = load_file(_constants.LAST_RUN_PATH)
        # Remove existing last_run.json file
        remove(_constants.LAST_RUN_PATH)

    # Create a new last_run.json file 
    new_data = {"lastRun": _constants.NOW}

    with open(_constants.LAST_RUN_PATH, 'w') as file:
        file.write(json.dumps(new_data, indent=_constants.JSON_INDENT))

    # Return lastRun timestamp
    return last_run["lastRun"]