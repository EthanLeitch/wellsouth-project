# General modules
import logging
from os import environ

# Internet modules
import requests
import yagmail

# Security-related modules
from dotenv import dotenv_values

# Load .env values
config = dotenv_values(".env")

# Conform to ISO 8601
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('tcpserver')
logger.info(f"Program started via {environ['SHELL']}")

yag = yagmail.SMTP(config["EMAIL_ADDRESS"], config["EMAIL_PASSWORD"])
contents = [
    "Some random content...",
]
yag.send(config["RECEIVING_ADDRESS"], 'Test Email', contents)

"""
url = "https://api.bamboohr.com/api/gateway.php/companyDomain/v1/employees/changed"
response = requests.get(url)
print(response.text)
"""