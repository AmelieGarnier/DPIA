# DPIA — Gestion RH & Données de Santé

> **Statut :** DPIA Obligatoire — Art. 35 RGPD  
> **Risque global :** ÉLEVÉ  
> **Articles concernés :** Art. 9, Art. 32, Art. 35 RGPD  
> **DPD :** Obligatoire

---

## 1. Contexte et description du traitement

| Élément | Détail |
|---|---|
| Responsable de traitement | Entreprise industrielle (350 salariés) |
| Finalité | Gestion administrative des ressources humaines |
| Système | SIRH (Système d'Information des Ressources Humaines) |
| Base légale | Obligation légale (Art. 6(1)(c)) + consentement pour certaines catégories |
| Catégories de données | Identité, salaires, arrêts maladie, RQTH, fiches d'aptitude, visites médicales |
| Hébergement | Cloud privé — **HDS requis** pour les données de santé |
| Nombre de personnes | 350 salariés |

---

## 2. Évaluation des critères de nécessité de DPIA (CNIL)

| Critère | Présent | Justification |
|---|---|---|
| Évaluation / scoring | ✅ | Non |
| Décision automatisée | ✅ | Non |
| Surveillance systématique | ✅ | Non |
| Données sensibles (Art. 9) | ✔ | Santé (arrêts maladie, RQTH, aptitudes), handicap |
| Données à grande échelle | ✔ | 350 salariés, données multi-catégories |
| Croisement de données | ✔ | SIRH croisé avec paie, médecine du travail, prévoyance |
| Personnes vulnérables | ✔ | Salariés en situation de handicap (RQTH) |
| Usage innovant | ✅ | Non |
| Entrave à l'exercice d'un droit | ✔ | Impact potentiel sur l'emploi |

**Score : 5/9 critères — DPIA OBLIGATOIRE** + **DPD désigné obligatoire** (Art. 37(1)(b))

---

## 3. Identification des risques

### Risque 1 — Accès non autorisé aux données de santé

| Élément | Évaluation |
|---|---|
| **Description** | Un employé RH sans habilitation spécifique accède aux diagnostics ou arrêts maladie |
| **Vraisemblance** | Modérée (2/4) |
| **Impact** | Critique (4/4) — discrimination possible |
| **Niveau de risque** | **ÉLEVÉ** |
| **Mesure corrective** | Contrôle d'accès granulaire (RBAC), cloisonnement des données médicales |

### Risque 2 — Hébergement hors HDS

| Élément | Évaluation |
|---|---|
| **Description** | Données de santé hébergées sur un cloud non certifié HDS |
| **Vraisemblance** | Faible (1/4) — si contrôle préalable effectué |
| **Impact** | Critique (4/4) — infraction pénale (Art. L.1111-8 CSP) |
| **Niveau de risque** | **CRITIQUE** |
| **Mesure corrective** | Vérification certificat HDS de l'hébergeur, clause contractuelle obligatoire |

### Risque 3 — Fuite de données via export SIRH

| Élément | Évaluation |
|---|---|
| **Description** | Export CSV ou Excel contenant des données de santé envoyé par email non chiffré |
| **Vraisemblance** | Élevée (3/4) |
| **Impact** | Élevé (3/4) |
| **Niveau de risque** | **ÉLEVÉ** |
| **Mesure corrective** | Interdiction des exports non chiffrés, politique DLP, formation RH |

---

## 4. Mesures techniques et organisationnelles (Art. 32)

### Mesures techniques
- [ ] Chiffrement AES-256 des données au repos
- [ ] TLS 1.3 pour les communications SIRH
- [ ] RBAC (Role-Based Access Control) — accès médical restreint au médecin du travail
- [ ] Pseudonymisation des données pour les exports analytiques
- [ ] MFA sur le SIRH pour tous les profils RH
- [ ] Journalisation des accès aux données de santé (audit trail 2 ans)
- [ ] Surveillance Wazuh sur les serveurs SIRH

### Mesures organisationnelles
- [ ] DPD désigné et déclaré à la CNIL
- [ ] Contrat avec l'hébergeur incluant clause HDS + Art. 28 RGPD
- [ ] Politique de gestion des habilitations formalisée
- [ ] Formation annuelle des équipes RH (sensibilisation RGPD)
- [ ] Procédure de notification des violations (Art. 33/34)

---

## 5. Avis du DPD

> **Recommandation :** Traitement autorisé sous condition de :
> 1. Obtention du certificat HDS de l'hébergeur actuel
> 2. Mise en place du RBAC avec cloisonnement strict des données médicales
> 3. Formation des équipes RH dans les 3 mois

| Champ | Valeur |
|---|---|
| Date de l'analyse | Juin 2026 |
| Version | 1.0 |
| Prochaine revue | Juin 2027 |
| Statut | Conditionnel — 3 mesures à implémenter |

---

*Portfolio GRC — M2 ERIS — Document pédagogique*
