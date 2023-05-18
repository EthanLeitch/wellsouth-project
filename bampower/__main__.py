# Main program

# Internal module imports
import _constants
import _common
import requests

def main():
    for entry in _constants.watching:
        payload = {}

        payload["title"] = entry["title"]
        payload["fields"] = []

        for field in entry["fields"]:
            payload["fields"].append(field["alias"])

        response = _common.request_url("POST", "/v1/reports/custom?format=JSON&onlyCurrent=true", payload)

        print(response.text)

if __name__ == "__main__":
    main()