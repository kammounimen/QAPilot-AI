Base URL : http://localhost:8080


## GET /api/room
- Auth : aucune
- Succès : 200, JSON `{"rooms": [ ... ]}`
- Champs d'une chambre : roomid (int), roomName (str), type (Single|Double|Suite),
  roomPrice (int), accessible (bool), description (str), features (list[str]), image (str)
- roomid (int, 1 à 3) est DIFFÉRENT de roomName (str, "101" à "103").
- Chambres initiales :
  - roomid 1 / roomName "101" / Single / 100
  - roomid 2 / roomName "102" / Double / 150
  - roomid 3 / roomName "103" / Suite / 225
- Avec un jeton valide (cookie `token`), le résultat est identique : 200 et la même liste.
- OBSERVÉ : 200 et la même liste, avec ou sans jeton, y compris avec un jeton invalide.


## POST /api/room
- Auth : cookie `token=<jeton>` obligatoire
- Corps : {"roomName": str, "type": str, "accessible": bool, "description": str,
  "image": str, "roomPrice": int, "features": [str]}
- Sans jeton : 401, {"errors": ["Authentication required"]}
- Avec jeton : 200, {"success": true} (pas d'id renvoyé : retrouver la chambre via GET /api/room par roomName)


## GET /api/branding
- Auth : aucune
- Succès : 200, JSON contenant les infos de l'hôtel (non détaillées ici : tester uniquement le code 200 et le type JSON)


## POST /api/auth/login
- Auth : aucune
- Corps : {"username": "admin", "password": "password"}
- Succès : 200, {"token": "<chaîne>"}. Le jeton est dans le corps JSON, PAS dans un Set-Cookie.
- Le jeton est ensuite envoyé en cookie `token` sur les endpoints protégés.
- Mauvais mot de passe, mauvais identifiants ou champs vides : 401, {"error": "Invalid credentials"}
- ATTENDU pour un JSON invalide : 400
- OBSERVÉ pour un JSON invalide : 500, {"error": "An unexpected error occurred"} (voir DEF-001)


## GET /api/message
- Auth : cookie `token=<jeton>`
- Succès (avec jeton valide) : 200, {"messages": [{"id": int, "name": str, "read": bool, "subject": str}]}
- Donnée initiale : 1 message (id 1, James Dean, "Booking enquiry", non lu)
- Comportement ATTENDU (REQ-012) : 401 ou 403 sans jeton valide.
- Comportement OBSERVÉ : 200 sans jeton et avec jeton invalide (DEF-002).
- Les tests vérifient l'ATTENDU, jamais l'observé.


## Observations hors périmètre des tests

- DELETE d'une chambre : l'URL utilisée par l'interface n'est pas relevée. Ne pas générer de test.
  - Direct service room : DELETE http://localhost:3001/room/<roomid> -> 202 (hors proxy, ne pas utiliser)
  - Via 8080 : GET et DELETE /api/room/<roomid> -> 500 en texte brut
- Format d'erreur incohérent : /api/auth/login renvoie {"error": "..."} (chaîne),
  /api/room renvoie {"errors": ["..."]} (liste). Mineur.