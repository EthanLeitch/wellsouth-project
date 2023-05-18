# Common functions imported by different modules
import _constants

import requests

def request_url(request_type, url_end, payload=None):
    '''Function for sending a GET/POST request'''
    url = f"https://api.bamboohr.com/api/gateway.php/{_constants.config['DOMAIN']}{url_end}"

    if request_type == "GET":
        if payload:
            response = requests.get(url, json=payload, headers=_constants.HEADERS)
        else:
            response = requests.get(url, headers=_constants.HEADERS)
    
    if request_type == "POST":
        if payload:
            response = requests.post(url, json=payload, headers=_constants.HEADERS)
        else:
            response = requests.post(url, headers=_constants.HEADERS)
    
    return response