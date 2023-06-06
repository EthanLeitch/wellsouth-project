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
from os import rename
import json
from datetime import datetime
from deepdiff import DeepDiff
import pathlib

_file_validator.main()

metafields = _file_validator.load_file(_constants.METAFIELDS_PATH)
watching = _file_validator.load_file(_constants.WATCHING_PATH)

def parse(string):
    string = string.lower()
    string = string.replace(" ", "_")
    return string

def main():
    # Download all 'watching' fields and save them to current snapshot directory
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
    
    print("Sorting snapshots...")

    snapshots = []

    # Check each snapshot folder in snapshots directory has the correct timestamp
    for file_path in list(pathlib.Path(_constants.SNAPSHOTS_PATH).iterdir()):
        try:
            datetime.strptime(file_path.name, "%Y-%m-%d_%H-%M-%S")
            snapshots.append(file_path.name)
        except ValueError as e:
            _logging.logger.warning(f"Unexpected file in snapshots directory: {e}")

    # Finish if we've only got one snapshot, because we don't need to compare them.
    if len(snapshots) == 1:
        _logging.shut_down()
    
    # Sort the snapshots from oldest to newest
    snapshots.sort(key=lambda x: datetime.strptime(x, "%Y-%m-%d_%H-%M-%S"))
    
    # Compare the current snapshot to the last snapshot
    last_snapshot_path = f"{_constants.SNAPSHOTS_PATH}{snapshots[-2]}"

    # Error handling: Watch for renames
    old_watching = _file_validator.load_file(f"{last_snapshot_path}/watching.json")
    difference = DeepDiff(old_watching, watching)

    if difference != {}:
        for count, key in enumerate(difference["values_changed"]):
            
            if "title" in key:
                d = difference["values_changed"][key]
                print(f"watching.json: title field has changed from {d['old_value']} to {d['new_value']}. Renaming files...")
                rename(f"{last_snapshot_path}/{d['old_value']}.json", f"{last_snapshot_path}/{d['new_value']}.json")

    # Compare each old snapshot to the new snapshot
    for entry in watching:
        old_snapshot = _file_validator.load_file(f"{last_snapshot_path}/{entry['title']}.json")         
        new_snapshot = _file_validator.load_file(f"{_constants.CURRENT_SNAPSHOT_PATH}{entry['title']}.json")

        # TODO: Error handling here if an employee is deleted (see slide 46).

        '''
        Edge Cases:
        - watching.json is modified (new fields added, title field changed, etc...)
        For normal operation, filenames in old_snapshot and new_snapshot need to remain the same, and match the 'title' field.
        Let's create a backup of watching.json in each snapshot folder.

        - an employee is deleted
        I'm not sure how this affects the program yet, so I'll need to test it.
        '''

        output = {
            "employees": [

            ]
        }

        for count, new_data in enumerate(new_snapshot["employees"]):

            old_data = (old_snapshot["employees"][count])

            difference = DeepDiff(old_data, new_data)

            output["employees"].append(new_data)

            for _, field in enumerate(entry["fields"]):
                output["employees"][count].pop(field["alias"])
            
            if difference == {}:
                # print(f"No updates for employee {new_data['id']}")
                output["employees"][count]["new_values"] = None
                output["employees"][count]["old_values"] = None
            else:
                # print(f"Update detected in employee {new_data['id']}")
                output["employees"][count]["new_values"] = difference["values_changed"]["root['jobTitle']"]["new_value"]
                output["employees"][count]["old_values"] = difference["values_changed"]["root['jobTitle']"]["old_value"]
            
            #output["employees"].append("new_values")

        print(output)

        # TODO: Add code here to POST output to power automate endpoints
        
        # response = requests.post(entry["sendToEndpoint"], headers=_constants.HEADERS, json=output)

    # Exit operations can go here...
    _logging.shut_down()

if __name__ == "__main__":
    main()