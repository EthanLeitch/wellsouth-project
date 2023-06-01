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
import pathlib
from datetime import datetime
from deepdiff import DeepDiff

_file_validator.main()

metafields = _file_validator.load_file(_constants.METAFIELDS_PATH)
watching = _file_validator.load_file(_constants.WATCHING_PATH)
#snapshots = _file_validator.load_snapshots()

def parse(string):
    string = string.lower()
    string = string.replace(" ", "_")
    return string

def main():
    # Download all 'watching' fields and save them to current snapshot directory
    """
    for entry in watching:
        payload = {}

        payload["title"] = entry["title"]
        payload["fields"] = []

        for field in entry["fields"]:
            payload["fields"].append(field["alias"])

        response = _common.request_url("POST", "/v1/reports/custom?format=JSON&onlyCurrent=true", payload)

        file_path = f"{_constants.CURRENT_SNAPSHOT_PATH}{payload['title']}.json"

        print(f"Getting {payload['title']}")

        with open(file_path, 'w') as file:
            parsed_json = json.loads(response.text)
            file.write(json.dumps(parsed_json, indent = _constants.JSON_INDENT))
    """
    
    print("Sorting snapshots...")

    snapshots = []

    # Check each file_path in snapshots directory is the correct timestamp
    for file_path in list(pathlib.Path(_constants.SNAPSHOTS_PATH).iterdir()):
        try:
            datetime.strptime(file_path.name, "%Y-%m-%d_%H-%M-%S")
            snapshots.append(file_path.name)
        except ValueError as e:
            _logging.logger.warning(f"Unexpected file in snapshots directory: {e}")
    
    # Sort the snapshots from oldest to newest
    snapshots.sort(key=lambda x: datetime.strptime(x, "%Y-%m-%d_%H-%M-%S"))
    
    # Compare the current snapshot to the last snapshot
    last_snapshot_path = f"{_constants.SNAPSHOTS_PATH}{snapshots[-2]}/"

    for entry in watching:
        # TODO: Error handling here if JSON file does not exist (see slide 46)
        old_snapshot = _file_validator.load_file(f"{last_snapshot_path}{entry['title']}.json")         
        new_snapshot = _file_validator.load_file(f"{_constants.CURRENT_SNAPSHOT_PATH}{entry['title']}.json")

        output = {
            "employees": [

            ]
        }

        for count, new_data in enumerate(new_snapshot["employees"]):

            old_data = (old_snapshot["employees"][count])

            difference = DeepDiff(old_data, new_data)

            output["employees"].append(new_data)
            
            if difference == {}:
                # print(f"No updates for employee {new_data['id']}")
                output["employees"][count]["new_values"] = None
            else:
                # print(f"Update detected in employee {new_data['id']}")
                output["employees"][count]["new_values"] = difference["values_changed"]["root['jobTitle']"]["new_value"]
                output["employees"][count]["old_values"] = difference["values_changed"]["root['jobTitle']"]["old_value"]
            
            #output["employees"].append("new_values")

        print(output)

        # TODO: Add code here to POST output to power automate endpoints

    # Exit operations can go here...
    # _logging.shut_down()

if __name__ == "__main__":
    main()