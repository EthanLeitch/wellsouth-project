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
FILES_PATH = path.join(absolute_path, "..", "files")
SNAPSHOTS_PATH = path.join(FILES_PATH, "snapshots")
METAFIELDS_PATH = path.join(FILES_PATH, "metafields.json")
WATCHING_PATH = path.join(FILES_PATH, "watching.json")
LAST_RUN_PATH = path.join(FILES_PATH, "last_run.json")
LOG_PATH = path.join(FILES_PATH, "log.txt")

# Set up time (ISO 8601)
now = datetime.datetime.now()

def timestamp(format, time=now):
    '''Returns a timestamp string'''
    if format == "filesafe":
        return time.strftime("%Y-%m-%d_%H-%M-%S")
    elif format == "bamboo":
        return time.strftime("%Y-%m-%dT%H:%M:%SZ")

LAST_RUN = _file_validator.load_last_run()

CURRENT_SNAPSHOT_PATH = path.join(SNAPSHOTS_PATH, timestamp('filesafe'))

WATCHING_TEMPLATE = """[
    {
        "title": "updated_job_title",
        "sendToEndpoint": "example.com",
        "fields": [
            {
                "id": 17,
                "name": "Job Title",
                "type": "list",
                "alias": "jobTitle"
            }
        ]
    }
]
"""

WATCHING_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "sendToEndpoint": {"type": "string"},
            "fields": {
                "type": "array",
                "properties": {
                    "id": {"type": ["integer", "string"]},
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "alias": {"type": "string"}
                },
                "required": ["id"],
                "additionalProperties": False
            }
        },
        "required": ["title", "sendToEndpoint", "fields"],
        "additionalProperties": False
    }
}

# Load .env values
env = dotenv_values(".env")

raw_key = env["API_KEY"] + ":" # Append : to API key otherwise it doesn't work
key_bytes = raw_key.encode('ascii') # Encode raw key to bytes
key_base64 = base64.urlsafe_b64encode(key_bytes) # Make it urlsafe base64
API_KEY = key_base64.decode("utf-8") # Decode back to utf-8

HEADERS = {
    "Accept": "application/json",
    "authorization": ("Basic " + API_KEY)
}
