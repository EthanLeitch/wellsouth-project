# Internal module imports
import _file_validator
import _logging

# Imports
import base64
import datetime
from os import path
from dotenv import dotenv_values

# Number defaults
JSON_INDENT = 4

# Set up file paths and templates
absolute_path = path.dirname(__file__)
FILES_PATH = path.join(absolute_path, "../files")
SNAPSHOTS_PATH = f"{FILES_PATH}/snapshots/"
METAFIELDS_PATH = f"{FILES_PATH}/metafields.json"
WATCHING_PATH = f"{FILES_PATH}/watching.json"
LAST_RUN_PATH = f"{FILES_PATH}/last_run.json"

# Set up time (ISO 8601)
now = datetime.datetime.now()
#TIME_FORMAT = ""
TIME_FORMAT = "%Y-%m-%d-%H:%M:%S"

def timestamp(format, time=now):
    if format == "filesafe":
        return time.strftime("%Y-%m-%d_%H-%M-%S")
    elif format == "bamboo":
        return time.strftime("%Y-%m-%dT%H:%M:%SZ")

NOW = now.strftime(TIME_FORMAT)
LAST_RUN = _file_validator.load_last_run()

#CURRENT_SNAPSHOT_PATH = f"{FILES_PATH}/snapshots/{timestamp('filesafe')}/"
CURRENT_SNAPSHOT_PATH = f"{FILES_PATH}/snapshots/2023-05-30_13-34-57/"

WATCHING_TEMPLATE = """[
    {
        "title": "updated_job_title",
        "sendToEndpoint": "example.com",
        "fields": [
            {
                "name": "Job Title",
                "type": "list",
                "alias": "jobTitle"
            }
        ]
    }
]
"""

# Load .env values
config = dotenv_values(".env")

raw_key = config["API_KEY"] + ":" # Append : to API key otherwise it doesn't work
key_bytes = raw_key.encode('ascii') # Encode raw key to bytes
key_base64 = base64.urlsafe_b64encode(key_bytes) # Make it urlsafe base64
API_KEY = key_base64.decode("utf-8") # Decode back to utf-8

HEADERS = {
    "Accept": "application/json",
    "authorization": ("Basic " + API_KEY)
}
