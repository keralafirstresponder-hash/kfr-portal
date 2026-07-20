#!/usr/bin/env bash
# Pull latest code, install deps, build the frontend, restart the backend.
# Run as the `kfr` user after the initial setup.sh finished.
set -euo pipefail

APP_DIR="/home/kfr/app"
cd "$APP_DIR"

echo "==> Pulling latest code..."
git pull --ff-only

# ---- Backend ----
echo "==> Setting up Python venv & installing backend deps..."
cd "$APP_DIR/backend"
python3.11 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Ensure .env exists (copy example on first run)
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit backend/.env before continuing:"
    echo "    nano $APP_DIR/backend/.env"
    exit 1
fi

# ---- Frontend ----
echo "==> Building React frontend..."
cd "$APP_DIR/frontend"
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit frontend/.env before continuing:"
    echo "    nano $APP_DIR/frontend/.env"
    exit 1
fi
yarn install --frozen-lockfile
yarn build

# ---- Restart backend service ----
echo "==> Restarting kfr-backend service..."
sudo systemctl restart kfr-backend
sudo systemctl status kfr-backend --no-pager --lines=5

echo ""
echo "✅ Deploy complete. Visit https://keralafirstresponder.org"
