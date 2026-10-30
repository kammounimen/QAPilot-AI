# Défauts observés

Les défauts décrivent un écart entre le comportement observé du site et le
comportement attendu défini par les exigences (requirements/REQ-xxx.md).


## DEF-001 : JSON invalide sur le login renvoie 500 au lieu de 400
- Endpoint : POST /api/auth/login
- Reproduction : envoyer le corps `{bad` avec l'en-tête `Content-Type: application/json`
- Attendu : 400 (erreur du client)
- Observé : 500, `{"error":"An unexpected error occurred"}`
- Gravité : mineure
- Exigence liée : REQ-001
- Test automatisé : TC-001-04 (tests/gold/test_def_001.py, rouge volontairement)
- Statut : ouvert


## DEF-002 : GET /api/message accessible sans jeton valide
- Endpoint : GET /api/message
- Reproduction : appeler l'endpoint sans cookie, ou avec le cookie `token=invalid_token`
- Attendu : 401 ou 403 (REQ-012)
- Observé : 200, avec la liste des messages (id, nom, sujet, état lu/non lu)
- Contraste : POST /api/room sans jeton renvoie bien 401 `{"errors":["Authentication required"]}`
- Gravité : moyenne à haute (exposition de données de visiteurs, en lecture seule)
- Exigences liées : REQ-010, REQ-012
- Tests automatisés (rouges volontairement) :
  - TC-012-02b : lecture des messages sans jeton (tests/gold/test_def_002.py)
  - TC-012-03b : lecture des messages avec jeton invalide (tests/gold/test_def_002.py)
- Statut : ouvert
- Réserve : il peut s'agir d'un choix de conception des auteurs de l'application.
  Le défaut est établi par rapport à notre exigence REQ-012, pas par rapport à leur intention.


## Écarts de génération (pas des défauts de l'application)

- TC-002-03, TC-012-01 et TC-012-02 attendent 401/403 sur `GET /api/room` sans jeton ou avec jeton invalide.
  Or REQ-002 décrit une liste de chambres visible par un visiteur (publique), et REQ-012 ne protège que
  la création, la modification, la suppression de chambres et la lecture des messages.
  Conclusion : cas incohérents avec les exigences (erreur de gen_cases), pas de défaut applicatif.
  Les tests sont marqués xfail via tests/known_gaps.py. Correction de fond : améliorer le prompt de gen_cases.