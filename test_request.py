import requests
import base64

# Security-related modules
from dotenv import dotenv_values

# Load .env values
config = dotenv_values(".env")

url = f"https://api.bamboohr.com/api/gateway.php/{config['DOMAIN']}/v1/employees/directory"

API_KEY = config["API_KEY"] + ":" # Append : to API key otherwise it doesn't work
# Encode API_KEY to base64
api_key_bytes = API_KEY.encode('ascii')
api_key_base64 = base64.urlsafe_b64encode(api_key_bytes)

#payload = {"displayName": "John Doe"}
headers = {
    "Accept": "application/json",
    "authorization": ("Basic " + (api_key_base64.decode("utf-8")))
}

response = requests.get(url, headers=headers)

print(response)
print(response.text)