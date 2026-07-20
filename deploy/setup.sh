#!/usr/bin/env bash
# One-shot VPS setup for Kerala First Responders (Mission 100K).
# Tested on Hostinger KVM 2 with Ubuntu 22.04 LTS.
# Run once as root on a fresh VPS:  bash setup.sh
set -euo pipefail

echo "==> Updating system..."
apt-get update && apt-get -y upgrade

echo "==> Installing base packages..."
apt-get install -y curl wget git build-essential ufw nginx certbot python3-certbot-nginx \
    python3.11 python3.11-venv python3-pip \
    libgl1 libglib2.0-0 libsm6 libxrender1

echo "==> Installing Node 20 (for building the React frontend)..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
npm install -g yarn

echo "==> Installing MongoDB 7 (Community Edition)..."
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" \
    | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
apt-get update
apt-get install -y mongodb-org
systemctl enable --now mongod

echo "==> Configuring firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

echo "==> Creating deploy user..."
id -u kfr &>/dev/null || useradd -m -s /bin/bash kfr
mkdir -p /home/kfr/app && chown -R kfr:kfr /home/kfr

echo ""
echo "✅ Base VPS setup complete."
echo ""
echo "Next steps:"
echo "  1. su - kfr"
echo "  2. git clone <your-repo> /home/kfr/app"
echo "  3. cd /home/kfr/app && bash deploy/deploy.sh"
echo "  4. Copy deploy/nginx.conf → /etc/nginx/sites-available/kfr && link and reload"
echo "  5. certbot --nginx -d keralafirstresponder.org -d www.keralafirstresponder.org"
