# Internal module imports
import _logging
import _constants
import _common

# Imports
from os import path, remove
import requests
from requests.exceptions import InvalidURL
import json
import pathlib
import validators
import traceback
from jsonschema import validate


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
            exit()
    else:
        # Check that the URL is a valid url
        watching = _common.load_file(_constants.WATCHING_PATH)

        # Validate watching.json schema
        try:
            validate(watching, schema=_constants.WATCHING_SCHEMA)
        except Exception as e:
            _logging.shut_down("error")

        # Raise InvalidURL error if url is not valid
        for entry in watching:
            if not validators.url(entry["sendToEndpoint"]):
                try:
                    raise InvalidURL(f"watching.json: {entry['sendToEndpoint']} is not a valid URL.")
                except Exception:
                    _logging.shut_down("error")


def load_last_run():
    '''Return timestamp that the program was last run'''
    if not path.exists(_constants.LAST_RUN_PATH):
        # last_run.json does not exist, so lastRun should be now
        last_run = {"lastRun": _constants.timestamp('filesafe')}
    else:
        # Load existing last_run.json file
        last_run = _common.load_file(_constants.LAST_RUN_PATH)
        # Remove existing last_run.json file
        remove(_constants.LAST_RUN_PATH)

    # Create a new last_run.json file 
    new_data = {"lastRun": _constants.timestamp('filesafe')}

    with open(_constants.LAST_RUN_PATH, 'w') as file:
        file.write(json.dumps(new_data, indent=_constants.JSON_INDENT))

    # Return lastRun timestamp
    return last_run["lastRun"]