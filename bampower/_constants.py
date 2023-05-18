# Internal module imports
import _file_validator

# Imports
import base64
import json
from json import JSONDecodeError
import datetime
from os import path
from dotenv import dotenv_values

NOW = datetime.datetime.now()
# print(NOW.strftime("%Y-%m-%dT%H:%M:%SZ"))

# Set up file paths and templates
absolute_path = path.dirname(__file__)
FILES_PATH = path.join(absolute_path, "../files")
METATABLES_PATH = f"{FILES_PATH}/metatables.json"
WATCHING_PATH = f"{FILES_PATH}/watching.json"

WATCHING_TEMPLATE = """[
    {
        "title": "Updated Job Title",
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

_file_validator.main()

# Simple load_file function with error handling
def load_file(path):
    with open(path, 'r') as file:
        try:
            return json.load(file)
        except JSONDecodeError as e:
            print(f"Error in file {path}")
            print(f"JSONDecodeError: {e}")
            exit()

metatables = load_file(METATABLES_PATH)
watching = load_file(WATCHING_PATH)