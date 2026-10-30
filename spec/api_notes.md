## POST /api/auth/login
- Auth : aucune
- Corps : {"username": "admin", "password": "password"}
- Succès : 200, JSON {"token": "<chaîne>"} (pas de Set-Cookie)
- Mauvais mot de passe : 401, {"error": "Invalid credentials"}
- JSON invalide : 500 (voir DEF-001)

## GET /api/message
- Auth : cookie `token=<jeton>`
- Succès : 200, {"messages": [{"id": int, "name": str, "read": bool, "subject": str}]}
- Donnée initiale : 1 message (James Dean, "Booking enquiry", non lu)
