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
import traceback

_file_validator.main()

metafields = _common.load_file(_constants.METAFIELDS_PATH)
watching = _common.load_file(_constants.WATCHING_PATH)


def main():
    download()
    last_snapshot_path = sort_snapshots()
    
    # Skip if there's only 1 snapshot
    if last_snapshot_path != None:
        compare_snapshots(last_snapshot_path)
    
    _logging.shut_down()


def download():
    '''Download all 'watching' fields and save them to current snapshot directory'''
    for entry in watching:
        payload = {}

        payload["title"] = entry["title"]
        payload["fields"] = []

        for field in entry["fields"]:
            payload["fields"].append(field["id"])

        response = _common.request_url("POST", "/v1/reports/custom?format=JSON&onlyCurrent=true", payload)

        file_path = path.join(_constants.CURRENT_SNAPSHOT_PATH, f"{payload['title']}.json")

        print(f"Getting {payload['title']}")

        with open(file_path, 'w') as file:
            parsed_json = json.loads(response.text)

            # Check that we recieved as many fields as we got
            if len(entry["fields"]) != len(parsed_json["fields"]):
                print(f"{entry['title']} did not recieve all fields. Check that fields have the correct keys.")
                _logging.shut_down("error")
            
            # Rename "id" to "employee_id" to avoid conflicts with metafields that only have id keys
            for field in parsed_json["employees"]:
                field["employee_id"] = field.pop("id")
                            
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
    
    last_snapshot_path = path.join(_constants.SNAPSHOTS_PATH, snapshots[-2])

    """
    # Error handling: Watch for changes between old watching.json and latest one
    old_watching = _common.load_file(path.join(last_snapshot_path, "watching.json"))

    difference = DeepDiff(old_watching, watching)

    if difference != {}:
        print("watching.json: File has been modified. Please remove all previous snapshots, and run the program again.")
        _logging.error("watching.json: File has been modified. Please remove all previous snapshots, and run the program again.")
        _logging.shut_down("error", trace=False)
    """

    # Rename .json files if their name changes in watching.json
    old_watching = _common.load_file(path.join(last_snapshot_path, "watching.json"))
    difference = DeepDiff(old_watching, watching)

    if difference != {}:
        if "values_changed" in difference:
            for count, key in enumerate(difference["values_changed"]):
                if "title" in key:
                    d = difference["values_changed"][key]
                    print(f"watching.json: title field has changed from {d['old_value']} to {d['new_value']}. Renaming files...")
                    _logging.logger.warning(f"watching.json: title field has changed from {d['old_value']} to {d['new_value']}. Renaming files...")
                    rename(path.join(last_snapshot_path, f"{d['old_value']}.json"), path.join(last_snapshot_path, f"{d['new_value']}.json"))
    
    return last_snapshot_path


def compare_snapshots(last_snapshot_path):
    '''Compare each old snapshot to the new snapshot'''

    for entry in watching:
        try:
            old_snapshot = _common.load_file(path.join(last_snapshot_path, f"{entry['title']}.json"))
        except FileNotFoundError:
            # Old .json does not exist, so let's skip comparing it, as it is a newly-created .json
            print(f"New item ({entry['title']}) added to watching.json, skipping without posting...")
            continue
        
        new_snapshot = _common.load_file(path.join(_constants.CURRENT_SNAPSHOT_PATH, f"{entry['title']}.json"))

        output = {
            "employees": [

            ]
        }

        # Iterate over all employees
        for count, new_data in enumerate(new_snapshot["employees"]):

            old_data = (old_snapshot["employees"][count])

            difference = DeepDiff(old_data, new_data, ignore_type_in_groups=[(int, str, None)])

            output["employees"].append(new_data)

            # Remove all key-value pairs from employee save for employee_id (we'll add some of them back later)
            for item in list(output["employees"][count]):
                if item != "employee_id":
                    output["employees"][count].pop(item)

            new_values = []
            old_values = []
            
            if difference == {}:
                # No updates for this employee, so we can skip them
                # print(f"No updates for employee {new_data['employee_id']}")
                for _ in enumerate(entry["fields"]):
                    new_values.append(None)
                    old_values.append(None)
            else:
                # Fill "new_values" and "old_values" with their respective values from the difference dictionary
                print(f"Update detected in employee {new_data['employee_id']}")

                for _, key in enumerate(entry["fields"]):
                    if "values_changed" in difference:
                        # Check if individual key has an update or not
                        if (key['id'] in str(difference['values_changed'])):
                            # This could be better -- root['value'] is hardcoded
                            new_values.append(difference["values_changed"][f"root['{key['id']}']"]["new_value"])
                            old_values.append(difference["values_changed"][f"root['{key['id']}']"]["old_value"])
                        else:
                            # No updates for this specific key, so write None
                            new_values.append(None)
                            old_values.append(None)
                    else:
                        # Else, the field has (probably) been recently or modified within watching.json, so we can just write None.
                        new_values.append(None)
                        old_values.append(None)

            # Add new_values and old_values to employee table
            output["employees"][count]["new_values"] = new_values
            output["employees"][count]["old_values"] = old_values

        output = json.dumps(output)
        
        print(f"POSTING: {output}")

        """
        # Post to Power Automate...
        response = requests.post(entry["sendToEndpoint"], headers={"Accept": "application/json"}, json=output)
        print(f"RESPONSE: {response}")
        """


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        _logging.shut_down("error")