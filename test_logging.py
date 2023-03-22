import logging
from os import environ
import requests

# Conform to ISO 8601
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('tcpserver')
logger.info(f"Program started via {environ['SHELL']}")

url = "https://api.bamboohr.com/api/gateway.php/companyDomain/v1/employees/changed"

response = requests.get(url)

print(response.text)