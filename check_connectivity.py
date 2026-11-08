"""Teste la connexion à Jira Cloud et à Xray Cloud à partir du fichier .env.

Usage : python check_connectivity.py
Ne jamais afficher les secrets : le script n'imprime que des statuts.
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request


def load_env(path=".env"):
    if not os.path.exists(path):
        sys.exit("Fichier .env introuvable dans le dossier courant.")
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            # Le .env l'emporte sur d'éventuelles variables restées dans le terminal.
            os.environ[key.strip()] = value.strip().strip('"').strip("'")


def call(url, headers=None, data=None):
    req = urllib.request.Request(url, headers=headers or {}, data=data)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]
    except Exception as e:  # réseau, DNS, proxy...
        return None, str(e)


def main():
    load_env()
    url = os.environ.get("JIRA_URL", "").rstrip("/")
    user = os.environ.get("JIRA_USER", "")
    token = os.environ.get("JIRA_API_TOKEN", "")
    project = os.environ.get("JIRA_PROJECT_KEY", "")
    cid = os.environ.get("XRAY_CLIENT_ID", "")
    secret = os.environ.get("XRAY_CLIENT_SECRET", "")

    basic = base64.b64encode(f"{user}:{token}".encode()).decode()
    auth = {"Authorization": f"Basic {basic}", "Accept": "application/json"}

    print(f"Site Jira : {url}")

    # 1. Authentification Jira
    status, body = call(f"{url}/rest/api/3/myself", auth)
    if status == 200:
        print(f"[OK]  Jira : connecté en tant que {json.loads(body).get('emailAddress') or user}")
    else:
        print(f"[ERR] Jira auth : HTTP {status} - {body[:150]}")
        print("      401 = email/token faux ; 404 = mauvaise JIRA_URL.")
        return

    # 2. Accès au projet
    status, body = call(f"{url}/rest/api/3/project/{project}", auth)
    if status == 200:
        info = json.loads(body)
        print(f"[OK]  Projet {project} trouvé (style : {info.get('style')}, "
              f"type : {info.get('projectTypeKey')})")
    else:
        print(f"[ERR] Projet {project} : HTTP {status} - {body[:150]}")

    # 3. Type de ticket Test (installé par Xray)
    status, body = call(f"{url}/rest/api/3/issuetype", auth)
    if status == 200:
        names = [t["name"] for t in json.loads(body)]
        print(f"[OK]  Type 'Test' présent : {'Test' in names}  "
              f"(False = Xray pas installé sur ce site)")
    else:
        print(f"[ERR] Types de ticket : HTTP {status}")

    # 4. Authentification Xray
    if not cid or not secret:
        print("[--]  Xray : XRAY_CLIENT_ID / XRAY_CLIENT_SECRET vides, étape ignorée.")
        return
    payload = json.dumps({"client_id": cid, "client_secret": secret}).encode()
    status, body = call(
        "https://xray.cloud.getxray.app/api/v2/authenticate",
        {"Content-Type": "application/json"},
        payload,
    )
    if status == 200:
        print("[OK]  Xray : authentification réussie (JWT reçu).")
    else:
        print(f"[ERR] Xray auth : HTTP {status} - {body[:150]}")
        print("      401/403 = clés Xray fausses ou créées sur un autre site.")


if __name__ == "__main__":
    main()