# General modules
import logging
from os import environ
import time

# Internet modules
import requests
import yagmail

# Security-related modules
from dotenv import dotenv_values

# Load .env values
config = dotenv_values(".env")

# Conform to ISO 8601
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(filename="log.txt", format=FORMAT, level=logging.INFO)
logger = logging.getLogger()
logger.info(f"Program started via {environ['SHELL']}")

def critical_error():
    logger.warning("Something went wrong! Sending email message...")

    yag = yagmail.SMTP(config["EMAIL_ADDRESS"], config["EMAIL_PASSWORD"])
    contents = [
        "Something went wrong! The Python program has been automatically halted.",
        "Below this message is the program's log (log.txt). It may help with diagnosing the problem."
        " ",
    ]
    yag.send(config["RECEIVING_ADDRESS"], f'Python error @ {time.asctime()}', contents, attachments="log.txt")

    exit()

# critical_error()

"""
url = "https://api.bamboohr.com/api/gateway.php/companyDomain/v1/employees/changed"
response = requests.get(url)
print(response.text)
"""