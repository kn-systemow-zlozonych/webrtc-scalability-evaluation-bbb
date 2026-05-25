import hashlib
import os
import sys
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()
BBB_URL = (os.getenv("BBB_URL") or "").strip()
BBB_SECRET = (os.getenv("BBB_SECRET") or "").strip()

if not BBB_URL or not BBB_SECRET:
    print("BŁĄD: Brak zmiennych w pliku .env")
    sys.exit(1)

def generate_join_url(fullname, password):
    base_url = BBB_URL.rstrip('/')
    if not base_url.endswith("api"):
        base_url += "/api"

    params_dict = {
        "meetingID": "test-docker",
        "fullName": fullname,
        "password": password,
        "joinViaHtml5": "true"
    }

    query_string = urlencode(params_dict)
    payload = "join" + query_string + BBB_SECRET
    checksum = hashlib.sha1(payload.encode('utf-8')).hexdigest()

    return f"{base_url}/join?{query_string}&checksum={checksum}"

if __name__ == "__main__":
    mod_link = generate_join_url("Ja (Administrator)", "mp")
    bot_link = generate_join_url("Tester (Uczestnik)", "ap")

    print("\n" + "="*60)
    print("LINK MODERATORA (Pełne uprawnienia):")
    print(mod_link)
    print("\nLINK UCZESTNIKA (To, co widzą boty):")
    print(bot_link)
    print("="*60 + "\n")