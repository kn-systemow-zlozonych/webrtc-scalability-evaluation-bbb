import hashlib
import requests
import os
import sys
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

BBB_URL = (os.getenv("BBB_URL") or "").strip()
BBB_SECRET = (os.getenv("BBB_SECRET") or "").strip()

if not BBB_URL or not BBB_SECRET:
    print("ERROR: Make sure you have a .env file containing BBB_URL and BBB_SECRET")
    sys.exit(1)


def create_meeting():
    params_dict = {
        "name": "Test Docker Room",
        "meetingID": "test-docker",
        "attendeePW": "ap",
        "moderatorPW": "mp",
        "lockSettingsDisableCam": "false",
        "lockSettingsDisableMic": "false",
        "muteOnStart": "false",
        "record": "false"  #
    }

    query_string = urlencode(params_dict)

    payload = "create" + query_string + BBB_SECRET
    checksum = hashlib.sha1(payload.encode('utf-8')).hexdigest()

    base_url = BBB_URL.rstrip('/')
    if not base_url.endswith("api"):
        base_url += "/api"

    final_url = f"{base_url}/create?{query_string}&checksum={checksum}"

    print(f"Sending a request to: {base_url}...")

    try:
        response = requests.get(final_url)

        if response.status_code == 200:
            if "<returncode>SUCCESS</returncode>" in response.text:
                print(f"\nSUKCES! Room 'test-docker' created.")
                print(f"   Password user: ap")
            else:
                print(f"\nBigBlueButton API error (Logic):")
                print(response.text)
                print("\nTIP: Check that BBB_SECRET in the .env file is EXACTLY THE SAME")
                print("the output of the 'bbb-conf --secret' command on the server.")
        else:
            print(f"\nError HTTP: {response.status_code}")

    except Exception as e:
        print(f"\nErr: {e}")


if __name__ == "__main__":
    create_meeting()