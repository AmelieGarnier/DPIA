#!/bin/sh
# Docker entrypoint for the PIA CNIL container.
# POSIX sh compatible — no bash-specific syntax.

set -e

# ---------------------------------------------------------------------------
# 0. Dépendances système (git, python3, make, g++ absents dans node:18-alpine)
# ---------------------------------------------------------------------------
echo "[pia-init] Installation des dépendances système ..."
apk add --no-cache git python3 make g++
echo "[pia-init] Dépendances installées."

PIA_DIR="/app/pia"
PIA_REPO="https://github.com/LINCnil/pia.git"

# ---------------------------------------------------------------------------
# 1. Clone PIA if not already present (or clean up a partial clone)
# ---------------------------------------------------------------------------
if [ -f "${PIA_DIR}/package.json" ]; then
    echo "[pia-init] PIA repository already present at ${PIA_DIR}, skipping clone."
else
    # Nettoyer un éventuel clone partiel (ex: interrompu par un restart)
    # /app/pia est le point de montage du volume Docker → on vide le contenu,
    # on ne supprime pas le répertoire lui-même (interdit par le kernel)
    if [ -d "${PIA_DIR}" ]; then
        echo "[pia-init] Clone partiel détecté dans ${PIA_DIR}, nettoyage du contenu ..."
        find "${PIA_DIR}" -mindepth 1 -delete
        echo "[pia-init] Nettoyage terminé."
    fi
    echo "[pia-init] Cloning PIA from ${PIA_REPO} into ${PIA_DIR} ..."
    git clone --depth 1 "${PIA_REPO}" "${PIA_DIR}"
    echo "[pia-init] Clone complete."
fi

cd "${PIA_DIR}"

# ---------------------------------------------------------------------------
# 2. Install dependencies
# NODE_ENV=production est unset ici car Angular CLI est en devDependencies :
# npm install en mode production le skipperait et ng ne serait pas disponible.
# ---------------------------------------------------------------------------
echo "[pia-init] Installing dependencies ..."
unset NODE_ENV
if npm install --legacy-peer-deps; then
    echo "[pia-init] Dependencies installed."
else
    echo "[pia-init] 'npm install' failed, retrying without --legacy-peer-deps ..."
    npm install
    echo "[pia-init] Dependencies installed."
fi

# ---------------------------------------------------------------------------
# 3. Build the application (with fallbacks)
# ---------------------------------------------------------------------------
BUILD_SUCCESS=0

echo "[pia-init] Attempting production build with 'npm run build:prod' ..."
if npm run build:prod; then
    echo "[pia-init] Production build succeeded."
    BUILD_SUCCESS=1
else
    echo "[pia-init] 'npm run build:prod' failed, trying 'npm run build' ..."
    if npm run build; then
        echo "[pia-init] Build succeeded."
        BUILD_SUCCESS=1
    else
        echo "[pia-init] 'npm run build' also failed. Will start dev server instead."
    fi
fi

# ---------------------------------------------------------------------------
# 4. Serve the application
# ---------------------------------------------------------------------------
if [ "${BUILD_SUCCESS}" = "1" ]; then
    # Locate the built output directory (Angular commonly outputs to dist/<name>)
    DIST_DIR=""
    if [ -d "dist/pia-angular/browser" ]; then
        DIST_DIR="dist/pia-angular/browser"
    elif [ -d "dist/pia-angular" ]; then
        DIST_DIR="dist/pia-angular"
    elif [ -d "dist/pia" ]; then
        DIST_DIR="dist/pia"
    elif [ -d "dist/browser" ]; then
        DIST_DIR="dist/browser"
    else
        # Pick the first dist subdirectory found, if any
        DIST_DIR=$(find dist -maxdepth 1 -mindepth 1 -type d 2>/dev/null | head -n 1)
    fi

    if [ -n "${DIST_DIR}" ]; then
        echo "[pia-init] Serving built app from '${DIST_DIR}' on port 8080 ..."
        exec npx serve -s "${DIST_DIR}" -l 8080
    else
        echo "[pia-init] Build reported success but no dist directory found; falling back to dev server."
        BUILD_SUCCESS=0
    fi
fi

if [ "${BUILD_SUCCESS}" = "0" ]; then
    echo "[pia-init] Starting development server on port 8080 ..."
    exec npm start -- --port 8080 --host 0.0.0.0 --disable-host-check 2>/dev/null \
        || exec npm start
fi
