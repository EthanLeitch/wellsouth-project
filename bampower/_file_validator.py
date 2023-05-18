# Internal module imports
import _constants
import _common

# Imports
from os import path
import requests
import json

def main():
    if not path.exists(_constants.METATABLES_PATH):
        print(f"{_constants.METATABLES_PATH} not found. Downloading...")
        response = _common.request_url("GET", "/v1/meta/fields")

        with open(_constants.METATABLES_PATH, 'w') as file:
            parsed_json = json.loads(response.text)
            file.write(json.dumps(parsed_json, indent = 1))

    if not path.exists(_constants.WATCHING_PATH):
        print(f"{_constants.WATCHING_PATH} not found. Creating!")

        with open(_constants.WATCHING_PATH, 'w') as file:
            file.write(_constants.WATCHING_TEMPLATE)
