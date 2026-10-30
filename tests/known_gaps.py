# Cas générés incohérents avec les exigences : GET /api/room est public (REQ-002).
# Voir le registre des défauts, section "Écarts de génération".
INCONSISTENT_CASES = {
    "TC-002-03",
    "TC-012-01",
    "TC-012-02",
}
REASON = "Cas incohérent avec REQ-002/REQ-012 : GET /api/room est public (écart de génération, pas un défaut applicatif)"