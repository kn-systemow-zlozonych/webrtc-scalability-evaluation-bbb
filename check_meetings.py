import hashlib
import requests
import os
import sys
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()
BBB_URL = (os.getenv("BBB_URL") or "").strip()
BBB_SECRET = (os.getenv("BBB_SECRET") or "").strip()

if not BBB_URL or not BBB_SECRET:
    print("BŁĄD: Brak zmiennych w pliku .env")
    sys.exit(1)

base_url = BBB_URL.rstrip('/')
if not base_url.endswith("api"):
    base_url += "/api"


def get_meetings():
    method = "getMeetings"
    checksum = hashlib.sha1((method + BBB_SECRET).encode('utf-8')).hexdigest()
    url = f"{base_url}/{method}?checksum={checksum}"

    print(f"\nMEETINGS LIST LOADIN...")
    try:
        response = requests.get(url)
        root = ET.fromstring(response.text)

        if root.find("returncode").text == "SUCCESS":
            meetings = root.find("meetings").findall("meeting")
            if not meetings:
                print("No active meetings.")
            else:
                print(f" Found: {len(meetings)}")
                for m in meetings:
                    m_id = m.find("meetingID").text
                    m_name = m.find("meetingName").text
                    participant_count = m.find("participantCount").text
                    print(f"   - ID: '{m_id}' | Nazwa: '{m_name}' | Osób: {participant_count}")
        else:
            print("Error API:", response.text)
    except Exception as e:
        print(f"Error connection: {e}")


def check_meeting_status(meeting_id):
    method = "getMeetingInfo"
    params = urlencode({"meetingID": meeting_id, "password": "mp"})
    checksum = hashlib.sha1((method + params + BBB_SECRET).encode('utf-8')).hexdigest()
    url = f"{base_url}/{method}?{params}&checksum={checksum}"

    print(f"\nROOM STATUS: '{meeting_id}'...")
    try:
        response = requests.get(url)
        root = ET.fromstring(response.text)

        if root.find("returncode").text == "SUCCESS":
            is_running = root.find("running").text
            p_count = root.find("participantCount").text
            print(f"Room exists.")
            print(f"Status Running: {is_running}")
            print(f"Users: {p_count}")
        else:
            msg_key = root.find("messageKey").text if root.find("messageKey") is not None else "Error"
            if msg_key == "notFound":
                print(f"Room '{meeting_id}' NO LONGER EXISTS (has been closed or has expired).")
            else:
                print(f"Other err: {response.text}")

    except Exception as e:
        print(f"Błąd: {e}")


if __name__ == "__main__":
    get_meetings()

    check_meeting_status("test-docker")