# Main program

# Start logging
from os import environ
import _logging
_logging.logger.info(f"Program started via {environ['SHELL']}")

# Internal module imports
import _constants
import _common
import _file_validator

# External module imports
from os import path
import json

_file_validator.main()

metafields = _file_validator.load_file(_constants.METAFIELDS_PATH)
watching = _file_validator.load_file(_constants.WATCHING_PATH)
snapshots = _file_validator.load_snapshots()

def parse(string):
    string = string.lower()
    string = string.replace(" ", "_")
    return string

def main():
    for entry in watching:
        payload = {}

        payload["title"] = entry["title"]
        payload["fields"] = []

        for field in entry["fields"]:
            payload["fields"].append(field["alias"])

        response = _common.request_url("POST", "/v1/reports/custom?format=JSON&onlyCurrent=true", payload)

        file_path = f"{_constants.CURRENT_SNAPSHOT_PATH}{payload['title']}.json"

        if not path.exists(file_path):
            print(f"{file_path} not found. Creating!")

        with open(file_path, 'w') as file:
            parsed_json = json.loads(response.text)
            file.write(json.dumps(parsed_json, indent = _constants.JSON_INDENT))

if __name__ == "__main__":
    main()