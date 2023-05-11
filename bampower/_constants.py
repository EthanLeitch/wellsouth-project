# Internal module imports
import _file_validator

# Imports
import base64
import json
import datetime
from os import path
from dotenv import dotenv_values

NOW = datetime.datetime.now()
# print(NOW.strftime("%Y-%m-%dT%H:%M:%SZ"))

absolute_path = path.dirname(__file__)
FILES_PATH = path.join(absolute_path, "../files")
METATABLES_PATH = f"{FILES_PATH}/metatables.json"

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

METATABLES = _file_validator.main()