import hashlib
import requests
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()
BBB_URL = (os.getenv("BBB_URL") or "").strip()
BBB_SECRET = (os.getenv("BBB_SECRET") or "").strip()
base_url = BBB_URL.rstrip('/') + "/api" if not BBB_URL.endswith("api") else BBB_URL

def end_meeting(meeting_id, moderator_password):
    method = "end"
    params = urlencode({"meetingID": meeting_id, "password": moderator_password})
    checksum = hashlib.sha1((method + params + BBB_SECRET).encode('utf-8')).hexdigest()
    url = f"{base_url}/{method}?{params}&checksum={checksum}"

    print(f"Close ports '{meeting_id}'...")
    response = requests.get(url)
    print(response.text)

if __name__ == "__main__":
    # Remember: the password must be for the MODERATOR (mp), not for a participant (ap)
    end_meeting("test-docker", "mp")