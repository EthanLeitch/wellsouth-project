# Imports
import logging
from os import rename
import requests
import yagmail

import _constants

# Set up logging (ISO 8601)
LOGGING_FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(filename=f"{_constants.FILES_PATH}/log.txt", format=LOGGING_FORMAT, level=logging.INFO)
logger = logging.getLogger()

def shut_down():
    # Move log.txt to current snapshot folder
    rename(f"{_constants.FILES_PATH}/log.txt", f"{_constants.CURRENT_SNAPSHOT_PATH}/log.txt")

def send_mail():
    logger.info("Something went wrong! Sending email message...")

    yag = yagmail.SMTP(_constants.config["EMAIL_ADDRESS"], _constants.config["EMAIL_PASSWORD"])
    contents = [
        "Something went wrong! The Python program has been automatically halted.",
        "Below this message is the program's log (log.txt). It may help with diagnosing the problem."
        " ",
    ]
    yag.send(_constants.config["RECEIVING_ADDRESS"], f'Python error @ {time.asctime()}', contents, attachments="log.txt")

    exit()