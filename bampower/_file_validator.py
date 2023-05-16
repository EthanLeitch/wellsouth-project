# Internal module imports
import _constants

# Imports
from os import path
import requests
import json

def request_url(request, url_end, payload=None):
    '''Function for sending a GET/POST request'''
    url = f"https://api.bamboohr.com/api/gateway.php/{_constants.config['DOMAIN']}{url_end}"

    if request == "GET":
        if payload:
            response = requests.get(url, json=payload, headers=_constants.HEADERS)
        else:
            response = requests.get(url, headers=_constants.HEADERS)
    
    if request == "POST":
        if payload:
            response = requests.post(url, json=payload, headers=_constants.HEADERS)
        else:
            response = requests.post(url, headers=_constants.HEADERS)
    
    return response

def main():
    if not path.exists(_constants.METATABLES_PATH):
        print(f"{_constants.METATABLES_PATH} not found. Downloading...")
        response = request_url("GET", "/v1/meta/tables")

        with open(file_path, 'w') as file:
            parsed_json = json.loads(response.text)
            file.write(json.dumps(parsed_json, indent = 1))

    if not path.exists(_constants.EMPLOYEES_PATH):
        print(f"{_constants.EMPLOYEES_PATH} not found. Downloading...")
        response = request_url("POST", "/v1/reports/custom?format=JSON&onlyCurrent=true", 
        {
            "fields": ["firstName"],
            "title": "Report"
        })
        
        with open(_constants.EMPLOYEES_PATH, 'w') as file:
            parsed_json = json.loads(response.text)

            output = []

            for employee in parsed_json['employees']:
                output.append(employee['id'])

            file.write(json.dumps(output, indent = 1))