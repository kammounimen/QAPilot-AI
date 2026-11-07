import json
import os
import sys
import time
import urllib.error
import urllib.request

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
MAX_ATTEMPTS = 120
DELAY = 5

payload = json.dumps({"username": "admin", "password": "password"}).encode()

for i in range(1, MAX_ATTEMPTS + 1):
    req = urllib.request.Request(
        f"{BASE_URL}/api/auth/login",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            if r.status == 200:
                print(f"App prête : {BASE_URL} (login OK, tentative {i})")
                sys.exit(0)
    except (urllib.error.URLError, ConnectionError, TimeoutError, OSError):
        pass
    print(f"Attente de l'application ({i}/{MAX_ATTEMPTS})...")
    time.sleep(DELAY)

print("Application non prête : délai dépassé")
sys.exit(1)