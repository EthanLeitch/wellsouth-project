# Internal module imports
import _constants

# External module imports
import logging
from os import rename, remove, path
from shutil import copyfile, rmtree
import requests
import yagmail
import traceback
from rich.console import Console
console = Console()

# Set up logging (ISO 8601)
LOGGING_FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(filename=_constants.LOG_PATH, format=LOGGING_FORMAT, level=logging.INFO)
logger = logging.getLogger()


def shut_down(type="normal", trace=True):
    '''Move working files and shut down the program'''
    print()

    if type == "normal":
        # Move log.txt to current snapshot folder
        rename(_constants.LOG_PATH, path.join(_constants.CURRENT_SNAPSHOT_PATH, "log.txt"))

        # Copy watching.json to current snapshot folder
        copyfile(_constants.WATCHING_PATH, path.join(_constants.CURRENT_SNAPSHOT_PATH, "watching.json"))
        message_style = "green"

    elif type == "error":
        if trace:
            # Print traceback 
            traceback.print_exc()
            logger.error(traceback.format_exc())

        # Delete current snapshot 
        rmtree(_constants.CURRENT_SNAPSHOT_PATH)
        message_style = "red"
    
    elif type == "debug":
        # Delete current snapshot 
        rmtree(_constants.CURRENT_SNAPSHOT_PATH)
        message_style = "blue"

    console.print(f"Program ended ({type})", style=message_style)
    logging.info(f"Program ended ({type})")

    exit()


def send_mail():
    '''Send an email alert'''
    logger.info("Something went wrong! Sending email message...")

    yag = yagmail.SMTP(_constants.env["EMAIL_ADDRESS"], _constants.env["EMAIL_PASSWORD"])
    contents = [
        "Something went wrong! The Python program has been automatically halted.",
        "Below this message is the program's log (log.txt). It may help with diagnosing the problem."
        " ",
    ]
    yag.send(_constants.config["RECEIVING_ADDRESS"], f'Python error @ {time.asctime()}', contents, attachments="log.txt")

    exit()