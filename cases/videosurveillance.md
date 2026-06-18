# DPIA — Système de Vidéosurveillance PME

> **Statut :** DPIA Obligatoire — Art. 35 RGPD  
> **Risque global :** CRITIQUE  
> **Articles concernés :** Art. 9, Art. 32, Art. 35 RGPD

---

## 1. Contexte et description du traitement

| Élément | Détail |
|---|---|
| Responsable de traitement | PME industrielle (250 salariés) |
| Finalité | Sécurité des locaux, prévention des intrusions |
| Base légale | Intérêt légitime (Art. 6(1)(f) RGPD) |
| Nombre de caméras | 24 caméras IP intérieures et extérieures |
| Module IA | Analyse comportementale (détection de chutes, intrusions) |
| Durée de conservation | 30 jours (images), 1 an (métadonnées d'alertes) |
| Personnes concernées | Salariés (250), visiteurs, prestataires |

---

## 2. Évaluation des critères de nécessité de DPIA (CNIL)

| Critère | Présent | Justification |
|---|---|---|
| Évaluation / scoring | ✔ | Analyse comportementale IA |
| Décision automatisée | ✔ | Alertes automatiques envoyées aux vigiles |
| Surveillance systématique | ✔ | 24 caméras, couverture totale des locaux |
| Données sensibles (Art. 9) | ✔ | Données biométriques potentielles (visages) |
| Données à grande échelle | ✔ | 250+ personnes, flux continu 24h/24 |
| Croisement de données | ✅ | Non (système isolé) |
| Personnes vulnérables | ✅ | Non spécifiquement |
| Usage innovant | ✔ | Module IA comportemental |
| Entrave à l'exercice d'un droit | ✅ | Non |

**Score : 6/9 critères — DPIA OBLIGATOIRE** (seuil CNIL : ≥2 critères)

---

## 3. Identification des risques

### Risque 1 — Collecte de données biométriques non consentie

| Élément | Évaluation |
|---|---|
| **Description** | Le module IA peut générer des gabarits faciaux (données biométriques Art. 9) sans consentement explicite |
| **Vraisemblance** | Élevée (3/4) |
| **Impact** | Critique (4/4) |
| **Niveau de risque** | **CRITIQUE** |
| **Mesure corrective** | Désactiver la fonction de reconnaissance faciale OU obtenir le consentement explicite + DPD obligatoire |

### Risque 2 — Accès non autorisé aux flux vidéo

| Élément | Évaluation |
|---|---|
| **Description** | Accès aux flux en temps réel ou aux enregistrements par des personnes non habilitées |
| **Vraisemblance** | Modérée (2/4) |
| **Impact** | Élevé (3/4) |
| **Niveau de risque** | **ÉLEVÉ** |
| **Mesure corrective** | MFA sur l'interface d'administration, chiffrement des flux (TLS 1.3), journalisation des accès |

### Risque 3 — Conservation excessive des données

| Élément | Évaluation |
|---|---|
| **Description** | Conservation des enregistrements au-delà des 30 jours réglementaires |
| **Vraisemblance** | Faible (1/4) |
| **Impact** | Modéré (2/4) |
| **Niveau de risque** | **FAIBLE** |
| **Mesure corrective** | Suppression automatique (purge CRON), procédure de contrôle mensuelle |

---

## 4. Mesures techniques et organisationnelles (Art. 32)

### Mesures techniques
- [ ] Chiffrement des flux vidéo (TLS 1.3 en transit, AES-256 au repos)
- [ ] MFA obligatoire sur l'interface d'administration NVR
- [ ] Réseau vidéosurveillance isolé (VLAN dédié)
- [ ] Purge automatique à J+30 (scripts CRON vérifiés)
- [ ] Journalisation de tous les accès aux enregistrements
- [ ] Surveillance Wazuh sur le serveur NVR

### Mesures organisationnelles
- [ ] Procédure d'habilitation formalisée (liste des accédants)
- [ ] Information des salariés (affichages RGPD conformément à l'Art. 13)
- [ ] Déclaration CNIL (consultation préalable si données biométriques activées)
- [ ] Revue annuelle de la DPIA
- [ ] DPD désigné si données biométriques traitées

---

## 5. Avis du DPD

> **Recommandation :** Désactiver le module d'analyse comportementale IA ou le restreindre à la détection de mouvements (sans génération de gabarits biométriques). En cas de maintien, engagement d'une consultation préalable CNIL (Art. 36 RGPD) obligatoire.

| Champ | Valeur |
|---|---|
| Date de l'analyse | Juin 2026 |
| Version | 1.0 |
| Prochaine revue | Juin 2027 |
| Statut | En attente de décision sur le module IA |

---

*Portfolio GRC — M2 ERIS — Document pédagogique*
