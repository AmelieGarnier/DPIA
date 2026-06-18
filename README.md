# Plateforme DPIA — Portfolio GRC M2 ERIS

![RGPD](https://img.shields.io/badge/RGPD-(UE)%202016%2F679-7c3aed?style=flat-square&logo=eu&logoColor=white)
![Art.35](https://img.shields.io/badge/Art.%2035-DPIA%20Obligatoire-ef4444?style=flat-square)
![Art.33](https://img.shields.io/badge/Art.%2033-Notification%2072h-f59e0b?style=flat-square)
![Art.32](https://img.shields.io/badge/Art.%2032-Sécurité%20du%20Traitement-00d4ff?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=flat-square&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose%20v2-2496ed?style=flat-square&logo=docker&logoColor=white)
![ISO27005](https://img.shields.io/badge/ISO%2027005-MONARC-00ff88?style=flat-square)

> **Cadre réglementaire :** RGPD (UE) 2016/679 — Articles 32, 33, 35  
> **Outils déployés :** PIA CNIL · MONARC ISO 27005 · Wazuh · Suricata · Shuffle · TheHive

---

## Présentation

Ce dépôt documente le déploiement et l’utilisation d’une plateforme DPIA (Data Protection Impact Assessment / Analyse d’Impact relative à la Protection des Données) à des fins d’apprentissage GRC. Il illustre comment articuler :

- L’**outil officiel PIA de la CNIL** pour conduire des analyses d’impact
- **MONARC** (ISO 27005) pour la modélisation et l’évaluation des risques
- La **stack SIEM/SOC** existante (Wazuh + Suricata + Shuffle + TheHive) comme couche de détection technique des violations de données

---

## Architecture globale

```
┌─────────────────────────────────────────────────────────────────┐
│                    COUCHE CONFORMITÉ RGPD                        │
│                                                                   │
│  ┌──────────────────┐          ┌──────────────────────────────┐  │
│  │   PIA CNIL       │          │   MONARC (ISO 27005)         │  │
│  │   :8080          │◄────────►│   :8888                      │  │
│  │  Analyse DPIA    │          │  Modélisation des risques     │  │
│  └──────────────────┘          └──────────────────────────────┘  │
│           │                                  │                    │
│           └──────────────┬───────────────────┘                   │
│                          │                                        │
│              ┌───────────▼────────────┐                        │
│              │   wazuh_dpia_bridge.py   │                        │
│              │  Lien SIEM ↔ RGPD Art.33 │                        │
│              └───────────┬────────────┘                        │
└──────────────────────────────│─────────────────────────────┘
                           │
┌─────────────────────────▼────────────────────────────────────┐
│                    COUCHE DÉTECTION TECHNIQUE                     │
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────────┐ │
│  │  Wazuh   │  │ Suricata │  │ Shuffle  │  │    TheHive      │ │
│  │ SIEM/EDR │→ │   IDS    │→ │  SOAR    │→ │ Case Management │ │
│  │  :55000  │  │ (passif) │  │  :3001   │  │    :9000        │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Structure du projet

```
DPIA/
├── docker-compose.yml        # Déploiement PIA CNIL (port 8080)
├── pia-init.sh               # Entrypoint Docker : clone + build + serve PIA
├── DEPLOYMENT.md             # Guide de déploiement complet (VM GRC 192.168.1.70)
├── cases/
│   ├── videosurveillance.md  # DPIA — Vidéosurveillance PME
│   ├── rh-sante.md           # DPIA — RH et données de santé
│   └── collectivite.md       # DPIA — SI collectivité territoriale
├── scripts/
│   └── wazuh_dpia_bridge.py  # Liaison Wazuh ↔ RGPD Art. 33
├── reports/                  # Rapports JSON/PDF générés (gitignorés)
└── portfolio/
    └── index.html            # Page vitrine GitHub Pages
```

---

## Prérequis

| Composant | Version minimale |
|---|---|
| Docker Engine | 24.x |
| Docker Compose | v2.x (plugin) |
| Python | 3.10+ |
| Wazuh Manager | 4.x (API activée) |

### Dépendances Python

```bash
pip install requests reportlab python-dateutil colorama
```

---

## Déploiement

### 1. Vérifier l’absence de conflits de ports

```bash
# Ports utilisés par ce projet : 8080 (PIA) et 8888 (MONARC)
ss -tlnp | grep -E '8080|8888'
# Doit retourner vide
```

### 2. Lancer la stack

```bash
git clone https://github.com/AmelieGarnier/DPIA.git
cd DPIA/
docker compose up -d
```

### 3. Vérifier l’état des conteneurs

```bash
docker compose ps
docker compose logs -f pia
```

### 4. Accès aux interfaces

| Outil | URL | Identifiants par défaut |
|---|---|---|
| PIA CNIL | `http://localhost:8080` | Aucun — application locale |
| MONARC | `http://localhost:8888` | `admin@admin.localhost` / `admin` |

> MONARC est déployé séparément via `monarc-local`. Voir [DEPLOYMENT.md](DEPLOYMENT.md) pour le guide complet.

---

## Utilisation du script `wazuh_dpia_bridge.py`

```bash
# Configuration via variables d’environnement
export WAZUH_HOST="192.168.1.50"
export WAZUH_PORT="55000"
export WAZUH_USER="wazuh-wui"
export WAZUH_PASS="<votre_mot_de_passe>"

# Exécution
cd DPIA/scripts/
python3 wazuh_dpia_bridge.py

# Le script génère :
#   ../reports/dpia_report_YYYYMMDD_HHMMSS.json
```

---

## Cas d’usage documentés

| Fichier | Traitement | Obligation DPIA |
|---|---|---|
| `cases/videosurveillance.md` | Vidéosurveillance PME | **Obligatoire** — données biométriques potentielles, surveillance systématique |
| `cases/rh-sante.md` | Gestion RH — données de santé | **Obligatoire** — données sensibles Art. 9 RGPD, DPD requis |
| `cases/collectivite.md` | SI collectivité territoriale | **Obligatoire** — 9/9 critères CNIL, 45 000 habitants |

---

## Cadre réglementaire

### Article 35 RGPD — Analyse d’Impact (DPIA)
Obligatoire lorsqu’un traitement est « susceptible d’engendrer un risque élevé pour les droits et libertés ». La CNIL a publié une [liste des traitements nécessitant une DPIA](https://www.cnil.fr/fr/les-analyses-dimpact-relatives-la-protection-des-donnees-aipd).

### Article 33 RGPD — Notification des violations sous 72h
Toute violation de données à caractère personnel doit être notifiée à l’autorité de contrôle (CNIL) **dans les 72 heures** suivant la prise de connaissance. Le script `wazuh_dpia_bridge.py` calcule automatiquement le délai restant.

### Article 32 RGPD — Sécurité du traitement
Mesures techniques et organisationnelles appropriées : chiffrement, pseudonymisation, tests réguliers. Wazuh + Suricata assurent la surveillance continue.

---

## Pipeline de détection des violations (Art. 33 RGPD)

```
Wazuh alerte niveau ≥12
        │
        ▼
Filtre catégories RGPD
(BDD, exfiltration, brute-force, ransomware)
        │
        ▼
Évaluation : violation probable ?
        │
   ┌────┴────┐
  OUI      NON
   │         │
   ▼         └──► Log et archivage
Shuffle playbook déclenché
   │
   ▼
Ticket TheHive créé
(tag : RGPD-Art33, délai 72h)
   │
   ▼
Rapport JSON → DPO (notification manuelle CNIL si confirmé)
```

---

## Avertissement

Ce projet est à vocation **pédagogique**. Les DPIAs documentées sont des exemples structurés et ne constituent pas des analyses juridiques opposables. Pour un déploiement en production, consultez un juriste spécialisé en protection des données.

---

*Dernière mise à jour : juin 2026 — Portfolio M2 ERIS*
