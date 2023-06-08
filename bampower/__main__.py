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
from os import path, rename
import json
from datetime import datetime
from deepdiff import DeepDiff
import pathlib
import requests

_file_validator.main()

metafields = _file_validator.load_file(_constants.METAFIELDS_PATH)
watching = _file_validator.load_file(_constants.WATCHING_PATH)


def main():
    download()
    last_snapshot_path = sort_snapshots()
    compare_snapshots(last_snapshot_path)
    _logging.shut_down()


def download():
    '''Download all 'watching' fields and save them to current snapshot directory'''
    for entry in watching:
        payload = {}

        payload["title"] = entry["title"]
        payload["fields"] = []

        for field in entry["fields"]:
            payload["fields"].append(field["alias"])

        response = _common.request_url("POST", "/v1/reports/custom?format=JSON&onlyCurrent=true", payload)

        file_path = path.join(_constants.CURRENT_SNAPSHOT_PATH, f"{payload['title']}.json")

        print(f"Getting {payload['title']}")

        with open(file_path, 'w') as file:
            parsed_json = json.loads(response.text)
            file.write(json.dumps(parsed_json, indent = _constants.JSON_INDENT))


def sort_snapshots():
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
        return
    
    # Sort the snapshots from oldest to newest
    snapshots.sort(key=lambda x: datetime.strptime(x, "%Y-%m-%d_%H-%M-%S"))
    
    last_snapshot_path = f"{_constants.SNAPSHOTS_PATH}{snapshots[-2]}"

    # Error handling: Watch for changes between old watching.json and latest one
    old_watching = _file_validator.load_file(path.join(last_snapshot_path, "watching.json"))
    difference = DeepDiff(old_watching, watching)

    if difference != {}:
        # print(difference)
        for count, key in enumerate(difference["values_changed"]):
            
            if "title" in key:
                d = difference["values_changed"][key]
                print(f"watching.json: title field has changed from {d['old_value']} to {d['new_value']}. Renaming files...")
                rename(path.join(last_snapshot_path, f"{d['old_value']}.json"), path.join(last_snapshot_path, f"{d['new_value']}.json"))

        # print("watching.json: schema has changed. Please remove all prior snapshots, and run the program again.")
    
    return last_snapshot_path


def compare_snapshots(last_snapshot_path):
    # Compare each old snapshot to the new snapshot
    for entry in watching:
        old_snapshot = _file_validator.load_file(path.join(last_snapshot_path, f"{entry['title']}.json"))
        new_snapshot = _file_validator.load_file(path.join(_constants.CURRENT_SNAPSHOT_PATH, f"{entry['title']}.json"))

        # TODO: Error handling here if an employee is deleted (see slide 46).

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
        
        response = requests.post(entry["sendToEndpoint"], headers=_constants.HEADERS, json=output)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Caught error in main: {e}")
        _logging.logger.error(f"Caught error in main: {e}")
        _logging.shut_down("error")