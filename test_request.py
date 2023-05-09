import requests
import base64
import json
import datetime

# Security-related modules
from dotenv import dotenv_values

NOW = datetime.datetime.now()
# print(NOW.strftime("%Y-%m-%dT%H:%M:%SZ"))


# Load .env values
config = dotenv_values(".env")

url = f"https://api.bamboohr.com/api/gateway.php/{config['DOMAIN']}/v1/meta/tables"

API_KEY = config["API_KEY"] + ":" # Append : to API key otherwise it doesn't work
# Encode API_KEY to base64
api_key_bytes = API_KEY.encode('ascii')
api_key_base64 = base64.urlsafe_b64encode(api_key_bytes)

# payload = {"displayName": "John Doe"}
headers = {
    "Accept": "application/json",
    "authorization": ("Basic " + (api_key_base64.decode("utf-8")))
}

response = requests.get(url, headers=headers)

print(response)


with open("files/metatables.json", 'w') as file:
    parsed_json = json.loads(response.text)
    file.write(json.dumps(parsed_json, indent=1))
