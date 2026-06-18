#!/usr/bin/env python3
"""
wazuh_dpia_bridge.py
Pont SIEM <-> RGPD : interroge l'API Wazuh, évalue si les alertes
constituent une violation de données personnelles (Art. 33 RGPD),
calcule le délai de notification CNIL (72h), et génère un rapport.

Configuration : variables d'environnement ou fichier scripts/.env.local
    WAZUH_HOST        IP/nom du Wazuh Manager      (défaut : 192.168.1.50)
    WAZUH_PORT        Port API Wazuh                (défaut : 55000)
    WAZUH_USER        Utilisateur API               (défaut : wazuh-wui)
    WAZUH_PASS        Mot de passe API
    ALERT_LEVEL_MIN   Niveau d'alerte minimum       (défaut : 12)
    LOOKBACK_HOURS    Fenêtre de recherche en h    (défaut : 24)

Codes de sortie :
    0   Aucune violation détectée
    1   Erreur technique (API, connexion)
    2   Violation confirmée ou délai 72h dépassé — action requise
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Dépendances optionnelles — installées via : pip install requests reportlab
# python-dateutil colorama
# ---------------------------------------------------------------------------
try:
    import requests
except ImportError:
    sys.exit("[ERREUR] Module 'requests' manquant. Lancer : pip install requests")

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    COLOR = True
except ImportError:
    COLOR = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CONFIG = {
    "host":         os.getenv("WAZUH_HOST",       "192.168.1.50"),
    "port":         os.getenv("WAZUH_PORT",       "55000"),
    "user":         os.getenv("WAZUH_USER",       "wazuh-wui"),
    "password":     os.getenv("WAZUH_PASS",       ""),
    "level_min":    int(os.getenv("ALERT_LEVEL_MIN", "12")),
    "lookback_h":   int(os.getenv("LOOKBACK_HOURS",  "24")),
}

REPORTS_DIR = Path(__file__).parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Mots-clés indicatifs d'une violation de données personnelles
DPIA_KEYWORDS = [
    "exfiltration", "data leak", "unauthorized access", "brute force",
    "sql injection", "ransomware", "personal data", "gdpr", "rgpd",
    "credential", "password dump", "database", "backup", "pii",
    "données personnelles", "accès non autorisé", "violation",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _color(text: str, color_code: str) -> str:
    if COLOR:
        return f"{color_code}{text}{Style.RESET_ALL}"
    return text


def info(msg: str):    print(f"[INFO]  {msg}")
def warn(msg: str):    print(_color(f"[WARN]  {msg}", Fore.YELLOW if COLOR else ""))
def error(msg: str):   print(_color(f"[ERROR] {msg}", Fore.RED if COLOR else ""), file=sys.stderr)
def ok(msg: str):      print(_color(f"[OK]    {msg}", Fore.GREEN if COLOR else ""))


# ---------------------------------------------------------------------------
# Authentification Wazuh
# ---------------------------------------------------------------------------
def get_token() -> str:
    url = f"https://{CONFIG['host']}:{CONFIG['port']}/security/user/authenticate"
    if not CONFIG["password"]:
        error("WAZUH_PASS non défini. Configurer scripts/.env.local.")
        sys.exit(1)
    try:
        resp = requests.post(
            url,
            auth=(CONFIG["user"], CONFIG["password"]),
            verify=False,
            timeout=10,
        )
        resp.raise_for_status()
        token = resp.json()["data"]["token"]
        ok("Authentification Wazuh réussie.")
        return token
    except requests.exceptions.ConnectionError:
        error(f"Impossible de joindre {CONFIG['host']}:{CONFIG['port']}. Vérifier la connectivité.")
        sys.exit(1)
    except Exception as exc:
        error(f"Erreur d'authentification : {exc}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Récupération des alertes
# ---------------------------------------------------------------------------
def fetch_alerts(token: str) -> list:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://{CONFIG['host']}:{CONFIG['port']}/security/events"
    params = {
        "limit": 500,
        "level": CONFIG["level_min"],
    }
    try:
        resp = requests.get(url, headers=headers, params=params, verify=False, timeout=15)
        if resp.status_code == 404:
            # Endpoint alternatif
            url = f"https://{CONFIG['host']}:{CONFIG['port']}/alerts"
            resp = requests.get(url, headers=headers, params=params, verify=False, timeout=15)
        resp.raise_for_status()
        data = resp.json().get("data", {}).get("affected_items", [])
        info(f"{len(data)} alerte(s) de niveau >= {CONFIG['level_min']} récupérée(s).")
        return data
    except Exception as exc:
        warn(f"Récupération alertes : {exc}. Poursuite avec 0 alerte.")
        return []


# ---------------------------------------------------------------------------
# Évaluation RGPD
# ---------------------------------------------------------------------------
def evaluate_rgpd(alerts: list) -> dict:
    """Détermine si les alertes constituent une violation Art. 33 RGPD."""
    matching = []
    for alert in alerts:
        description = (
            str(alert.get("rule", {}).get("description", "")).lower()
            + " "
            + str(alert.get("data", "")).lower()
        )
        if any(kw in description for kw in DPIA_KEYWORDS):
            matching.append(alert)

    if not matching:
        return {
            "violation_donnees_personnelles": "non",
            "alertes_concernees": 0,
            "categorie_donnees": None,
            "articles_concernes": [],
            "details": "Aucune alerte indicatrice d'une violation de données personnelles.",
        }

    # Heuristique de catégorisation
    descriptions = " ".join(
        a.get("rule", {}).get("description", "") for a in matching
    ).lower()

    if "exfiltration" in descriptions or "data leak" in descriptions:
        category = "Exfiltration de données personnelles"
        articles = ["Art. 33", "Art. 34"]
    elif "ransomware" in descriptions:
        category = "Chiffrement / destruction de données (ransomware)"
        articles = ["Art. 33"]
    elif "brute force" in descriptions or "credential" in descriptions:
        category = "Tentative d'accès non autorisé"
        articles = ["Art. 33"]
    else:
        category = "Accès ou modification non autorisée"
        articles = ["Art. 33"]

    # Horodatage de la première alerte concernée
    timestamps = [
        a.get("timestamp") or a.get("@timestamp")
        for a in matching if a.get("timestamp") or a.get("@timestamp")
    ]
    first_detection = min(timestamps) if timestamps else datetime.now(timezone.utc).isoformat()

    return {
        "violation_donnees_personnelles": "oui",
        "alertes_concernees": len(matching),
        "categorie_donnees": category,
        "articles_concernes": articles,
        "premiere_detection": first_detection,
    }


# ---------------------------------------------------------------------------
# Calcul du délai de notification (Art. 33 — 72h)
# ---------------------------------------------------------------------------
def compute_deadline(first_detection_iso: str) -> dict:
    try:
        if first_detection_iso.endswith("Z"):
            first_detection_iso = first_detection_iso[:-1] + "+00:00"
        detection_dt = datetime.fromisoformat(first_detection_iso)
    except (ValueError, AttributeError):
        detection_dt = datetime.now(timezone.utc)

    deadline = detection_dt + timedelta(hours=72)
    now = datetime.now(timezone.utc)
    remaining = deadline - now

    if remaining.total_seconds() <= 0:
        statut = "DEPASSE"
        heures_restantes = 0.0
    elif remaining.total_seconds() < 3600 * 12:
        statut = "URGENT"
        heures_restantes = round(remaining.total_seconds() / 3600, 1)
    else:
        statut = "EN COURS"
        heures_restantes = round(remaining.total_seconds() / 3600, 1)

    return {
        "premiere_detection": detection_dt.isoformat(),
        "echeance_72h": deadline.isoformat(),
        "heures_restantes": heures_restantes,
        "statut": statut,
        "action_requise": (
            "NOTIFIER CNIL IMMEDIATEMENT" if statut == "DEPASSE"
            else "Préparer la notification CNIL"
        ),
    }


# ---------------------------------------------------------------------------
# Génération du rapport
# ---------------------------------------------------------------------------
def generate_report(evaluation: dict, deadline_info: dict | None) -> dict:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report = {
        "rapport_genere": datetime.now(timezone.utc).isoformat(),
        "evaluation_rgpd": evaluation,
    }
    if deadline_info:
        report["delai_notification_cnil"] = deadline_info

    report_path = REPORTS_DIR / f"dpia_report_{timestamp}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    info(f"Rapport JSON sauvegardé : {report_path}")
    return report


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------
def main() -> int:
    print("=" * 60)
    print(" Wazuh DPIA Bridge — Art. 33 RGPD")
    print(f" Hôte Wazuh : {CONFIG['host']}:{CONFIG['port']}")
    print(f" Niveau min  : {CONFIG['level_min']} | Fenêtre : {CONFIG['lookback_h']}h")
    print("=" * 60)

    token = get_token()
    alerts = fetch_alerts(token)
    evaluation = evaluate_rgpd(alerts)

    deadline_info = None
    exit_code = 0

    if evaluation["violation_donnees_personnelles"] == "oui":
        warn(f"Violation détectée : {evaluation['categorie_donnees']}")
        deadline_info = compute_deadline(evaluation["premiere_detection"])
        statut = deadline_info["statut"]
        if statut in ("DEPASSE", "URGENT"):
            error(f"Délai 72h : {statut} — {deadline_info['action_requise']}")
        else:
            warn(f"Délai 72h : {deadline_info['heures_restantes']}h restantes")
        exit_code = 2
    else:
        ok(evaluation["details"])

    report = generate_report(evaluation, deadline_info)
    print("\n--- Résumé ---")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("-" * 60)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
