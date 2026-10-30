# Défauts observés

## DEF-001 : JSON invalide sur le login renvoie 500 au lieu de 400
- Endpoint : POST /api/auth/login
- Reproduction : envoyer le corps `{bad` avec `Content-Type: application/json`
- Attendu : 400 (erreur client)
- Observé : 500, `{"error":"An unexpected error occurred"}`
- Gravité : mineure
- Exigence liée : REQ-001
