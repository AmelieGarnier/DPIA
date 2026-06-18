# DPIA — SI Collectivité Territoriale

> **Statut :** DPIA Obligatoire — Art. 35 RGPD  
> **Risque global :** CRITIQUE  
> **Articles concernés :** Art. 6(1)(e), Art. 9, Art. 10, Art. 32, Art. 35 RGPD  
> **Population :** 45 000 habitants

---

## 1. Contexte et description du traitement

| Élément | Détail |
|---|---|
| Responsable de traitement | Commune de 45 000 habitants |
| Finalité | Gestion du SI municipal et services aux citoyens |
| Base légale | Mission d'intérêt public (Art. 6(1)(e) RGPD) |
| Périmètre | État civil, action sociale, urbanisme, portail citoyen FranceConnect |
| Données traitées | Identité, famille, revenus (CAF), santé (CCAS), casier judiciaire, données cadastrales |
| Systèmes concernés | SI état civil, CCAS, urbanisme, portail FranceConnect, messagerie |
| DPO | Obligatoire (Art. 37(1)(a)) — autorité publique |

---

## 2. Évaluation des critères de nécessité de DPIA (CNIL)

| Critère | Présent | Justification |
|---|---|---|
| Évaluation / scoring | ✔ | Évaluation sociale (CCAS) |
| Décision automatisée | ✔ | Traitement automatique des demandes d'aides sociales |
| Surveillance systématique | ✔ | Vidéoprotection voie publique |
| Données sensibles (Art. 9/10) | ✔ | Santé (CCAS), situations sociales, données judiciaires |
| Données à grande échelle | ✔ | 45 000 habitants |
| Croisement de données | ✔ | État civil ↔ CCAS ↔ urbanisme ↔ FranceConnect |
| Personnes vulnérables | ✔ | Allocataires sociaux, mineurs (état civil) |
| Usage innovant | ✔ | FranceConnect (identité numérique fédérée) |
| Entrave à l'exercice d'un droit | ✔ | Accès aux services publics conditionné au SI |

**Score : 9/9 critères — DPIA OBLIGATOIRE — Risque CRITIQUE**

---

## 3. Identification des risques

### Risque 1 — Compromission du portail FranceConnect

| Élément | Évaluation |
|---|---|
| **Description** | Usurpation d'identité via le flux OIDC FranceConnect, permettant l'accès aux services au nom d'un citoyen |
| **Vraisemblance** | Modérée (2/4) |
| **Impact** | Critique (4/4) — 45 000 citoyens potentiellement affectés |
| **Niveau de risque** | **CRITIQUE** |
| **Mesure corrective** | Validation des tokens OIDC, journalisation des connexions FranceConnect, alertes Wazuh sur anomalies d'authentification |

### Risque 2 — Exfiltration des données état civil

| Élément | Évaluation |
|---|---|
| **Description** | Vol de la base état civil (naissances, mariages, décès, filiation) |
| **Vraisemblance** | Faible (1/4) |
| **Impact** | Critique (4/4) — usurpation d'identité à grande échelle |
| **Niveau de risque** | **ÉLEVÉ** |
| **Mesure corrective** | Segmentation réseau, accès restreint au SI état civil, Suricata IDS sur le segment |

### Risque 3 — Ransomware sur le CCAS

| Élément | Évaluation |
|---|---|
| **Description** | Chiffrement des données sociales par un ransomware, blocage des versements d'aides |
| **Vraisemblance** | Modérée (2/4) |
| **Impact** | Critique (4/4) — personnes vulnérables sans ressources |
| **Niveau de risque** | **CRITIQUE** |
| **Mesure corrective** | Sauvegardes isolées (règle 3-2-1), EDR Wazuh, plan de continuité (PCA) testé annuellement |

### Risque 4 — Accès non autorisé aux dossiers sociaux

| Élément | Évaluation |
|---|---|
| **Description** | Agent municipal accédant aux dossiers sociaux de bénéficiaires hors de son périmètre |
| **Vraisemblance** | Modérée (2/4) |
| **Impact** | Élevé (3/4) |
| **Niveau de risque** | **ÉLEVÉ** |
| **Mesure corrective** | RBAC strict, traçabilité des accès, audit trimestriel des droits |

---

## 4. Mesures techniques et organisationnelles (Art. 32)

### Mesures techniques
- [ ] Segmentation réseau par métier (VLAN état civil, CCAS, urbanisme, DMZ FranceConnect)
- [ ] Chiffrement AES-256 des bases de données
- [ ] MFA sur tous les accès aux SI sensibles
- [ ] Wazuh EDR déployé sur tous les postes et serveurs
- [ ] Suricata IDS sur les segments réseau critiques
- [ ] Sauvegardes isolées (règle 3-2-1, test de restauration trimestriel)
- [ ] Journalisation centralisée (SIEM) avec rétention 1 an
- [ ] Surveillance des flux FranceConnect (tokens OIDC)

### Mesures organisationnelles
- [ ] DPO désigné et déclaré à la CNIL (Art. 37(1)(a) — autorité publique)
- [ ] Politique de gestion des habilitations par direction
- [ ] Formation annuelle de tous les agents traitant des données personnelles
- [ ] PCA/PRA testé annuellement
- [ ] Procédure de notification Art. 33 intégrée à Shuffle/TheHive
- [ ] Registre des traitements tenu à jour
- [ ] Révision annuelle de la DPIA

---

## 5. Exigences spécifiques — FranceConnect

L'intégration FranceConnect impose des obligations supplémentaires :

- Respect des CGU FranceConnect et de la politique de sécurité ANSSI
- Journalisation des événements d'authentification 12 mois minimum
- Notification immédiate à la DINUM en cas de compromission du flux OIDC
- Test d'intrusion annuel sur le composant d'intégration

---

## 6. Avis du DPO

> **Recommandation :** Traitement autorisé — la commune remplit ses obligations légales. La mise en œuvre du plan de mesures ci-dessus est obligatoire dans un délai de 6 mois. Un audit de sécurité extérieur (pentest) est fortement recommandé avant la mise en production du nouveau portail FranceConnect.

| Champ | Valeur |
|---|---|
| Date de l'analyse | Juin 2026 |
| Version | 1.0 |
| Prochaine revue | Juin 2027 |
| Statut | Autorisé — plan de mesures sous 6 mois |

---

*Portfolio GRC — M2 ERIS — Document pédagogique*
