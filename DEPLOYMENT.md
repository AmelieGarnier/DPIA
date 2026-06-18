# Déploiement de la plateforme DPIA

Guide de déploiement de la couche conformité RGPD du projet **DPIA** sur une VM dédiée (VM GRC), et son intégration avec la stack SOC existante.

| VM | Rôle | IP |
|---|---|---|
| VM Wazuh | Wazuh Manager + Suricata | `192.168.1.50` |
| VM SOAR | TheHive4 + Cortex3 + Elasticsearch + Shuffle | `192.168.1.60` |
| **VM GRC** ← ce guide | PIA CNIL + MONARC + `wazuh_dpia_bridge.py` | `192.168.1.70` |

---

## Table des matières

1. [Provisionnement de la VM GRC](#1-provisionnement-de-la-vm-grc)
2. [Initialisation système](#2-initialisation-système)
3. [Vérification de la connectivité réseau](#3-vérification-de-la-connectivité-réseau)
4. [Installation de Docker](#4-installation-de-docker)
5. [Récupération du dépôt](#5-récupération-du-dépôt)
6. [Déploiement de PIA CNIL](#6-déploiement-de-pia-cnil)
7. [Déploiement de MONARC via monarc-local](#7-déploiement-de-monarc-via-monarc-local)
8. [Vérification post-déploiement](#8-vérification-post-déploiement)
9. [Intégration SIEM ↔ RGPD](#9-intégration-siem--rgpd)
10. [Sécurisation](#10-sécurisation)
11. [Dépannage](#11-dépannage)
12. [Checklist](#12-checklist)

---

## 1. Provisionnement de la VM GRC

**Sur l'hyperviseur**

Créer une VM avec les spécifications suivantes :

| Ressource | Valeur |
|---|---|
| OS | Debian 13 (Trixie) 64-bit |
| RAM | 6 Go min (8 Go recommandés) |
| CPU | 4 vCPU |
| Disque | 40 Go |
| Réseau | Mode **pont (Bridged)**, même sous-réseau que `.50` et `.60` |

**VM GRC (192.168.1.70)** — configurer l'IP statique après l'installation Debian :

```bash
sudo nano /etc/network/interfaces
```

```
auto enp0s3
iface enp0s3 inet static
    address 192.168.1.70
    netmask 255.255.255.0
    gateway 192.168.1.1
    dns-nameservers 8.8.8.8
```

```bash
sudo systemctl restart networking
ip a | grep "inet "
# → 192.168.1.70/24 doit apparaître
```

---

## 2. Initialisation système

**VM GRC (192.168.1.70)**

```bash
sudo -i
apt update && apt upgrade -y
apt install -y curl gnupg jq ca-certificates git python3-pip python3-venv

# Alias DNS locaux (optionnel mais pratique)
cat >> /etc/hosts << 'EOF'
192.168.1.50  wazuh-vm
192.168.1.60  soar-vm
EOF
```

---

## 3. Vérification de la connectivité réseau

**VM GRC (192.168.1.70)**

```bash
# Test réseau vers la VM Wazuh
ping -c 3 192.168.1.50

# Test de l'API Wazuh (sans credentials)
curl -k -s https://192.168.1.50:55000/ | jq .title
# → "Unauthorized" = normal et attendu.
#   L'API répond et exige un token : la connectivité est confirmée.
```

> Si la commande `curl` time-out (et non `Unauthorized`), la VM Wazuh bloque
> peut-être la source `.70`. **Sur la VM Wazuh (192.168.1.50)** :
> ```bash
> sudo iptables -I INPUT -p tcp -s 192.168.1.70 --dport 55000 -j ACCEPT
> ```

---

## 4. Installation de Docker

**VM GRC (192.168.1.70)**

```bash
apt install -y ca-certificates curl gnupg lsb-release
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update
apt install -y docker-ce docker-ce-cli containerd.io \
               docker-buildx-plugin docker-compose-plugin

systemctl enable docker && systemctl start docker

# Vérification
docker --version
docker compose version
docker run hello-world
```

---

## 5. Récupération du dépôt

**VM GRC (192.168.1.70)**

```bash
git clone https://github.com/AmelieGarnier/DPIA.git ~/DPIA
cd ~/DPIA
ls
# → docker-compose.yml  pia-init.sh  scripts/  cases/  reports/  portfolio/
```

> Assure-toi que `pia-init.sh` est exécutable dans le repo :
> ```bash
> chmod +x pia-init.sh
> git add pia-init.sh && git commit -m "fix: rendre pia-init.sh exécutable" && git push
> ```

---

## 6. Déploiement de PIA CNIL

**VM GRC (192.168.1.70)**

### Architecture du déploiement

```
docker-compose.yml
└── service pia
    ├── image     : node:18-alpine (officielle Docker)
    ├── volume    : pia-app → /app/pia  (clone git + build Angular persistés)
    ├── entrypoint: pia-init.sh
    └── port      : 8080
```

`pia-init.sh` effectue automatiquement, dans l'ordre :
1. Clone de `https://github.com/LINCnil/pia.git` si absent
2. `npm ci --legacy-peer-deps` (ou `npm install` en repli)
3. Build `npm run build:prod` → `npm run build` → serveur de dev en dernier recours
4. Exposition du résultat sur le port 8080 via `npx serve` (ou `ng serve` en dev)

Le volume nommé `pia-app` couvre `/app/pia` : le clone et le build sont **persistés**
entre les redémarrages du conteneur. Seul le tout premier démarrage est long (~5 min).

### Lancement

```bash
cd ~/DPIA
docker compose up -d

# Suivre les logs en temps réel (premier démarrage : attendre la fin du build)
docker compose logs -f pia
```

**Ce qu'on attend dans les logs :**

```
[pia-init] Cloning PIA from https://github.com/LINCnil/pia.git ...
[pia-init] Clone complete.
[pia-init] Installing dependencies ...
[pia-init] Dependencies installed via 'npm ci'.
[pia-init] Attempting production build with 'npm run build:prod' ...
[pia-init] Production build succeeded.
[pia-init] Serving built app from 'dist/pia' on port 8080 ...
```

### Test

```bash
docker compose ps
# → pia-cnil   Up (healthy)

curl -s -o /dev/null -w "PIA CNIL → HTTP %{http_code}\n" http://localhost:8080/
# → PIA CNIL → HTTP 200
```

Accès depuis le navigateur : **`http://192.168.1.70:8080`**

> **Aucun identifiant requis.** PIA CNIL est une application locale sans authentification :
> les analyses sont stockées dans le navigateur (localStorage).

---

## 7. Déploiement de MONARC via monarc-local

**VM GRC (192.168.1.70)**

`monarc-local` est le lanceur officiel NC3-LU pour MONARC. Il encapsule sa propre
stack Docker Compose et expose des commandes simples (`up`, `status`, `logs`, `down`).
C'est l'option recommandée : pas d'image tierce, aucun secret à gérer dans le repo.

### 7.1 Téléchargement du paquet

Récupérer le `.deb` Linux depuis la **page officielle** :
→ [www.monarc.lu/documentation/technical-guide](https://www.monarc.lu/documentation/technical-guide/)
  (section "End-User installation" → Linux → `.deb`)

```bash
# Adapter le nom de fichier à la version disponible au moment du téléchargement
cd ~
wget https://<url-du-paquet-deb-depuis-la-doc-officielle>

# Installation
sudo apt install ./monarc-local_<version>_amd64.deb
```

Le paquet installe :
- les binaires dans `/opt/monarc-local`
- les commandes `monarc-local` et `monarc-local-gui` dans `/usr/bin`
- la config dans `~/.monarc-local/compose/.env`
- les données dans `~/.monarc-local/`

### 7.2 Vérification des prérequis

```bash
monarc-local doctor
# → doit signaler Docker OK, Compose plugin OK
#   Si un point est rouge : relire la section 4 et faire `newgrp docker`
```

### 7.3 Configuration

```bash
# Ouvrir la configuration générée automatiquement
nano ~/.monarc-local/compose/.env
```

**Paramètres obligatoires à vérifier/modifier :**

```bash
# 1. Versions (remplacer vX.Y.Z par un vrai tag de release)
#    Tags disponibles : https://github.com/monarc-project/MonarcAppFO/releases
MONARC_FO_VERSION=v2.13.4

# 2. Port d'écoute (rechercher la variable de port dans le .env)
grep -i port ~/.monarc-local/compose/.env
#    Modifier la valeur trouvée à 8888 pour cohérence avec ce projet
```

### 7.4 Démarrage

```bash
monarc-local up

# Attendre ~2-3 min (migrations de base de données au premier démarrage)
monarc-local status
# → monarc-frontoffice : running
# → monarc-db          : running
```

### 7.5 Accès et premier login

Accès depuis le navigateur : **`http://192.168.1.70:8888`**
(adapter le port si différent dans ton `.env`)

| Champ | Valeur par défaut |
|---|---|
| Email | `admin@admin.localhost` |
| Mot de passe | `admin` |

> **Changer immédiatement le mot de passe** après la première connexion :
> Profil → Changer le mot de passe.

### 7.6 Commandes utiles

```bash
monarc-local status                                     # état des conteneurs
monarc-local logs --service monarc-frontoffice --tail 200  # logs applicatifs
monarc-local update                                     # mise à jour MONARC
monarc-local down                                       # arrêt propre
```

> Les données MONARC vivent dans `~/.monarc-local/` — hors du repo Git.
> Aucun secret MONARC n'est à committer.

---

## 8. Vérification post-déploiement

**VM GRC (192.168.1.70)**

```bash
# État des conteneurs
docker compose ps                  # → pia-cnil : Up (healthy)
monarc-local status                # → monarc-frontoffice + monarc-db : running

# Tests HTTP
curl -s -o /dev/null -w "PIA CNIL → HTTP %{http_code}\n" http://localhost:8080/
curl -s -o /dev/null -w "MONARC   → HTTP %{http_code}\n" http://localhost:8888/
# → HTTP 200 dans les deux cas
```

| Outil | URL |
|---|---|
| PIA CNIL | `http://192.168.1.70:8080` |
| MONARC | `http://192.168.1.70:8888` |

---

## 9. Intégration SIEM ↔ RGPD

**VM GRC (192.168.1.70)**

```bash
# Prérequis Python (≥ 3.10 — vérifié sur Debian 13)
python3 --version

cd ~/DPIA/scripts/
python3 -m venv venv
source venv/bin/activate
pip install requests reportlab python-dateutil colorama
python3 -c "import requests, reportlab, dateutil, colorama; print('Dépendances OK')"
```

### Configuration

```bash
cat > ~/DPIA/scripts/.env.local << 'EOF'
WAZUH_HOST=192.168.1.50
WAZUH_PORT=55000
WAZUH_USER=wazuh-wui
WAZUH_PASS=<mot_de_passe_wazuh>
ALERT_LEVEL_MIN=12
LOOKBACK_HOURS=24
EOF

chmod 600 ~/DPIA/scripts/.env.local

# S'assurer que ce fichier n'est pas versionné
grep -q "scripts/.env.local" ~/DPIA/.gitignore \
  || echo "scripts/.env.local" >> ~/DPIA/.gitignore
```

### Wrapper d'exécution

```bash
cat > ~/DPIA/scripts/run_bridge.sh << 'EOF'
#!/bin/bash
# Lance wazuh_dpia_bridge.py avec les variables d'environnement chargées.
cd "$(dirname "$0")"
set -a && source .env.local && set +a
source venv/bin/activate
python3 wazuh_dpia_bridge.py
EOF
chmod +x ~/DPIA/scripts/run_bridge.sh
```

### Test de connectivité

```bash
source ~/DPIA/scripts/.env.local
curl -k -s -u "$WAZUH_USER:$WAZUH_PASS" \
  -X POST "https://$WAZUH_HOST:$WAZUH_PORT/security/user/authenticate" | jq .error
# → 0 = authentification réussie
```

### Exécution

```bash
~/DPIA/scripts/run_bridge.sh
echo "Code de sortie : $?"
# 0 = OK (pas d'action immédiate)
# 2 = violation confirmée ou délai 72h dépassé → action requise
```

Les rapports sont générés dans `~/DPIA/reports/` (JSON + PDF).

---

## 10. Sécurisation

**VM GRC (192.168.1.70)**

```bash
apt install -y ufw
ufw allow from 192.168.1.0/24 to any port 8080 proto tcp   # PIA CNIL
ufw allow from 192.168.1.0/24 to any port 8888 proto tcp   # MONARC
ufw allow ssh
ufw enable
ufw status
```

**Checklist secrets :**
- `scripts/.env.local` → exclu du repo via `.gitignore` ✓
- Données MONARC → dans `~/.monarc-local/` hors repo ✓
- Mot de passe MONARC → changé dès le premier login ✓
- Mot de passe Wazuh → jamais commité ✓

---

## 11. Dépannage

| Symptôme | Cause probable | Solution |
|---|---|---|
| `pia-cnil` : page blanche, aucune erreur | Build Angular en cours | Attendre 5 min, `docker compose logs -f pia` |
| `pia-cnil` : `Exiting(1)` | Erreur clone ou npm | `docker compose logs pia` → lire la ligne d'erreur |
| `pia-cnil` : rebuild à chaque restart | Volume monté sur le mauvais chemin | Vérifier que `docker-compose.yml` monte `pia-app:/app/pia` |
| Port 8080 déjà utilisé | Autre service sur la VM GRC | `ss -tlnp \| grep 8080`, changer le port hôte dans `docker-compose.yml` |
| `monarc-local doctor` : Docker KO | Utilisateur hors du groupe docker | `usermod -aG docker $USER && newgrp docker` |
| MONARC : page blanche après `up` | Migrations en cours (~2-3 min) | `monarc-local logs --service monarc-frontoffice --tail 50` |
| MONARC : port inaccessible | Port configuré différemment dans `.env` | `grep -i port ~/.monarc-local/compose/.env` |
| `curl` API Wazuh : timeout (pas `Unauthorized`) | Pare-feu VM Wazuh | Voir section 3 |
| Bridge : 0 alerte récupérée | Endpoint `/security/events` → peut nécessiter l'indexeur | Test manuel : voir note dans la section 9 |

---

## 12. Checklist

**Infrastructure**
- [ ] VM GRC créée, Debian 13, IP statique `192.168.1.70`, mode pont
- [ ] `curl` vers `192.168.1.50:55000` retourne `"Unauthorized"` (connectivité OK)
- [ ] Docker installé : `docker --version` + `docker compose version` OK

**PIA CNIL**
- [ ] `docker compose up -d` sans erreur
- [ ] `docker compose ps` → `pia-cnil` : `Up (healthy)`
- [ ] `http://192.168.1.70:8080` accessible depuis le navigateur

**MONARC**
- [ ] `monarc-local doctor` → tous les prérequis verts
- [ ] `monarc-local up` → `monarc-frontoffice` et `monarc-db` running
- [ ] `http://192.168.1.70:8888` accessible, mot de passe admin changé

**Bridge SIEM ↔ RGPD**
- [ ] Dépendances Python installées
- [ ] Authentification Wazuh testée (`curl` → `"error": 0`)
- [ ] `run_bridge.sh` → rapport JSON + PDF générés dans `reports/`

**Sécurité**
- [ ] `ufw` actif, ports 8080/8888 limités au sous-réseau
- [ ] Aucun secret commité dans le repo

---

*Projet DPIA — Portfolio GRC M2 ERIS*
