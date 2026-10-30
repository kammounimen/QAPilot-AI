import os
import sys
import time
import urllib.error
import urllib.request

from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("BASE_URL", "http://localhost:8080")

for i in range(1, 61):
    try:
        urllib.request.urlopen(url, timeout=5)
        print(f"App prête : {url}")
        sys.exit(0)
    except (urllib.error.URLError, ConnectionError, TimeoutError):
        print(f"Attente de l'application ({i}/60)...")
        time.sleep(5)

print("L'application n'a pas démarré", file=sys.stderr)
sys.exit(1)