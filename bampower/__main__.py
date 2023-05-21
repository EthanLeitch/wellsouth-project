# Main program

# Internal module imports
import _constants
import _common

# External module imports
from os import path
import json

def parse(string):
    string = string.lower()
    string = string.replace(" ", "_")
    return string

def main():
    for entry in _constants.watching:
        payload = {}

        payload["title"] = entry["title"]
        payload["fields"] = []

        for field in entry["fields"]:
            payload["fields"].append(field["alias"])

        response = _common.request_url("POST", "/v1/reports/custom?format=JSON&onlyCurrent=true", payload)

        file_path = f"{_constants.SNAPSHOTS_PATH}{payload['title']}.json"

        if not path.exists(file_path):
            print(f"{file_path} not found. Creating!")

        with open(file_path, 'w') as file:
            parsed_json = json.loads(response.text)
            file.write(json.dumps(parsed_json, indent = _constants.JSON_INDENT))

if __name__ == "__main__":
    main()