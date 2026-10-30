# QAPilot-AI

Pipeline de génération de tests API assistée par LLM, appliqué à l'application de réservation d'hôtel
*Restful Booker Platform* (lancée via Docker Compose).

Le principe : **exigences → cas de test → tests pytest**, avec des garde-fous pour vérifier que les tests
générés ne valident pas par erreur un comportement défectueux.

## Chaîne de traitement

```
requirements/REQ-xxx.md  ──gen_cases──▶  cases/REQ-xxx.json  ──gen_tests──▶  tests/api/test_tc_*.py
        (exigences)                       (cas de test, ne pas modifier)        (tests générés)
                                                    ▲
                              spec/api_notes.md + prompts/<version>/
```

| Étape | Fichier | Rôle |
|---|---|---|
| Génération des cas | `pipeline/gen_cases.py` | Produit `cases/REQ-*.json` à partir des exigences |
| Contrôle des cas | `pipeline/check_cases.py` | Valide la structure des cas |
| Génération des tests | `pipeline/gen_tests.py` | Produit un fichier pytest par cas dans `tests/api/` |
| Contrôle des tests | `pipeline/check_tests.py` | Garde-fous sur les tests générés (voir plus bas) |
| Client LLM | `pipeline/llm_client.py` | Appel à Groq (modèle `openai/gpt-oss-120b`), avec cache dans `.cache/llm/` |

## Structure du projet

```
cases/              Cas de test générés (jamais modifiés à la main)
requirements/       Exigences REQ-xxx.md
spec/api_notes.md   Notes sur l'API : endpoints, données, comportements ATTENDUS et OBSERVÉS
prompts/v1, v2      Prompts du générateur de tests (v2 = version actuelle)
pipeline/           Scripts de génération et de contrôle
tests/api/          Tests générés (ne pas modifier à la main)
tests/gold/         Tests écrits à la main (défauts connus, couverture manquante)
tests/conftest.py   Fixtures base_url, admin_token + hook xfail
tests/known_gaps.py Liste des cas générés incohérents avec les exigences
defects.md          Registre des défauts
```

## Prérequis

- Python et [uv](https://docs.astral.sh/uv/)
- Docker Desktop
- Un fichier `.env` avec la clé Groq (ne jamais le commiter)
- Optionnel : `BASE_URL` (par défaut `http://localhost:8080`)

## Utilisation

```powershell
# 1. Lancer l'application (démarrage lent : environ 70 s pour le service auth)
docker compose up -d

# 2. Générer les tests (consomme des tokens Groq)
uv run python -m pipeline.gen_tests

# 3. Contrôler
uv run ruff check --fix tests/api
uv run python -m compileall -q tests
uv run python -m pipeline.check_tests

# 4. Exécuter
uv run pytest tests/api tests/gold -q -rs
```

## Résultat actuel

```
3 failed, 14 passed, 3 xfailed
```

| Résultat | Tests | Signification |
|---|---|---|
| 3 failed | `tests/gold/test_def_001.py`, `test_def_002.py` | Vrais défauts de l'application (DEF-001, DEF-002), rouges volontairement |
| 3 xfailed | TC-002-03, TC-012-01, TC-012-02 | Cas générés incohérents avec les exigences (voir ci-dessous) |
| 14 passed | le reste | Relus : données correctes, aucun assert aligné sur un défaut |

## Défauts détectés

Détail dans `defects.md`.

| ID | Endpoint | Attendu | Observé | Gravité | Tests |
|---|---|---|---|---|---|
| DEF-001 | `POST /api/auth/login` avec JSON invalide | 400 | 500 | Mineure | TC-001-04 |
| DEF-002 | `GET /api/message` sans jeton ou avec jeton invalide | 401 ou 403 (REQ-012) | 200 + liste des messages | Moyenne à haute | TC-012-02b, TC-012-03b |

Autres constats : Swagger (`/swagger-ui.html`, `/v3/api-docs`) activé sous le profil `prod`, identifiants par
défaut `admin` / `password`, format d'erreur incohérent entre `/api/auth/login` (`error`) et `/api/room` (`errors`).

## Écarts de génération (pas des défauts de l'application)

TC-002-03, TC-012-01 et TC-012-02 attendent 401/403 sur `GET /api/room`. Or REQ-002 décrit une liste de chambres
visible par un visiteur (donc publique), et REQ-012 ne protège que la création, la modification et la suppression
de chambres ainsi que la lecture des messages. Ces cas sont une erreur de `gen_cases`. Ils sont marqués `xfail`
via `tests/known_gaps.py`, sans toucher aux fichiers générés.

## Règles de travail

1. **Ne jamais modifier `cases/` ni `tests/api/` à la main.** Les décisions vont dans `spec/`, `prompts/`,
   `tests/known_gaps.py` ou `tests/gold/`.
2. **Les tests vérifient le comportement attendu par les exigences**, jamais l'observé défectueux.
   Les défauts connus sont couverts par des tests gold écrits à la main.
3. **Le comportement attendu du cas fait foi, les données de test viennent des notes API** (identifiants,
   `roomid`, noms de champs). Voir `prompts/v2/gen_tests_api.md`.
4. **Un test vert ne prouve rien tant que son `assert` n'a pas été lu.**
5. **Ne pas régénérer sans raison** : le LLM varie d'un run à l'autre et chaque appel consomme le quota Groq
   (200 000 tokens par jour). Changer `PROMPT_VERSION` force une régénération sans vider le cache.

## Garde-fous (`pipeline/check_tests.py`)

Pour chaque fichier de `tests/api/` : compilation Python, marqueur `@pytest.mark.tc(...)` présent,
pas de `time.sleep`, pas d'appel externe, ruff sans erreur, et **aucun assert sur un code 5xx**
(signe d'un test aligné sur un bug).

## Problèmes rencontrés et enseignements

| Problème | Cause | Solution |
|---|---|---|
| Tests skippés « endpoint non documenté » | Cas ambigus et spec contradictoire | Spec consolidée, une section par endpoint |
| Tests verts mais faux (`GET /api/room` → 200) | Le modèle alignait le test sur les notes | Règle v2 : l'attendu du cas fait foi |
| Faux rouges (mauvais mot de passe, `roomid` 101) | Données inventées dans les cas recopiées | Règle v2 : données issues des notes |
| TC-001-04 asserté `== 500` | Le modèle a pris l'observé pour l'attendu | Test gold à la main + garde-fou 5xx |
| Fichier généré avec docstring non fermé | Variabilité du LLM | `compileall` + interdiction des docstrings dans le prompt |
| Erreur 429 Groq | Quota quotidien de tokens atteint | Changer de modèle, attendre, ne régénérer que si nécessaire |

## À faire

- Ajouter au prompt de `gen_cases` la règle « pas de cas 401/403 sur un endpoint public », régénérer les cas,
  puis vider `tests/known_gaps.py`.
- Couvrir la modification et la suppression de chambre (REQ-012, critère 1) une fois l'URL réelle relevée
  (`/api/room/<id>` renvoie 500 via le port 8080).
- Compléter la spec de `GET /api/branding`.
- Décider du sort de DEF-001 et DEF-002 avec l'équipe de l'application.
