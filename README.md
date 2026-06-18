# Plateforme DPIA — Portfolio GRC M2 ERIS

Déploiement et documentation d'une plateforme d'Analyse d'Impact sur la Protection des Données (AIPD) conforme RGPD, intégrée à une stack SOC/SIEM complète.

## Structure du dépôt

```
dpia/
├── docker-compose.yml       # Déploiement PIA CNIL
├── pia-init.sh              # Entrypoint du conteneur PIA
├── DEPLOYMENT.md            # Guide de déploiement complet
├── scripts/
│   └── wazuh_dpia_bridge.py # Pont SIEM ↔ RGPD (Art. 33)
├── cases/
│   ├── videosurveillance.md # DPIA Vidéosurveillance PME
│   ├── rh-sante.md          # DPIA RH & Données de Santé
│   └── collectivite.md      # DPIA SI Collectivité Territoriale
├── reports/                 # Rapports JSON/PDF générés
└── portfolio/
    └── index.html           # Page vitrine du projet
```

## Outils déployés

| Outil | Rôle | Port |
|---|---|---|
| PIA CNIL | Analyse d'impact RGPD (Art. 35) | 8080 |
| MONARC | Analyse de risques ISO 27005 | 8888 |
| Wazuh/SIEM | Détection violations de données | 55000 |
| Suricata/IDS | Détection d'intrusions réseau | — |
| Shuffle/SOAR | Automatisation de la réponse | 3001 |
| TheHive | Gestion des incidents RGPD | 9000 |

## Documentation

- [Guide de déploiement](DEPLOYMENT.md)
- [Page vitrine](portfolio/index.html)

---

*Document pédagogique — Portfolio M2 ERIS — Juin 2026*  
*Les analyses documentées sont des exemples structurés et ne constituent pas des avis juridiques opposables.*
