# Internal module imports
import _constants

# Imports
from os import path
import requests
import json

def main():
    if not path.exists(_constants.METATABLES_PATH):
        print("metatables.json not found. Downloading...")

        url = f"https://api.bamboohr.com/api/gateway.php/{_constants.config['DOMAIN']}/v1/meta/tables"

        response = requests.get(url, headers=_constants.HEADERS)
        
        with open(_constants.METATABLES_PATH, 'w') as file:
            parsed_json = json.loads(response.text)
            file.write(json.dumps(parsed_json, indent = 1))

    with open(_constants.METATABLES_PATH, 'r') as file:
        metatables = json.load(file)
        return metatables