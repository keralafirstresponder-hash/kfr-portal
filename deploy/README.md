# VPS Deployment — Kerala First Responders (Mission 100K)

Deploy the app on a **Hostinger KVM 2 VPS** (Ubuntu 22.04 LTS) with your `keralafirstresponder.org` domain.

## What you get

- Nginx → serves the built React frontend + reverse-proxies `/api/*` to FastAPI
- FastAPI backend (uvicorn, 2 workers) managed by `systemd` (auto-restart on crash/boot)
- MongoDB 7 running locally on the same box
- Free Let's Encrypt SSL certificate (auto-renews)
- **Optional** Resend for outgoing email (add anytime after launch)

## Prerequisites (Hostinger side)

1. **VPS bought**: KVM 2 with Ubuntu 22.04 LTS. Note the server's public IP.
2. **DNS** — in hPanel → Domains → `keralafirstresponder.org` → DNS/Nameservers → DNS Zone:
   - Delete any existing `A` records for `@` and `www`
   - Add:
     - `A   @    <VPS_PUBLIC_IP>   TTL 3600`
     - `A   www  <VPS_PUBLIC_IP>   TTL 3600`
3. Wait ~15 minutes for DNS propagation. Confirm with `nslookup keralafirstresponder.org`.

## One-time server setup

SSH into the VPS as root:

```bash
ssh root@<VPS_PUBLIC_IP>
```

Clone the repo and run the setup script:

```bash
apt update && apt install -y git
git clone https://github.com/<your-github-user>/keralafirstresponder.git /tmp/repo
bash /tmp/repo/deploy/setup.sh
```

The script installs: Nginx, Node 20, Python 3.11, MongoDB 7, Certbot, UFW firewall.

## Deploy the app

Switch to the `kfr` user, clone the repo into place, configure env, deploy:

```bash
su - kfr
git clone https://github.com/<your-github-user>/keralafirstresponder.git ~/app
cd ~/app
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 1) Generate JWT secret and edit the .env
JWT=$(openssl rand -hex 32) && sed -i "s|CHANGE_ME_LONG_RANDOM_STRING|$JWT|" backend/.env
nano backend/.env    # confirm MONGO_URL, PUBLIC_BASE_URL, leave RESEND_API_KEY empty for now

# 2) Kick off the build
bash deploy/deploy.sh
```

## Wire up systemd + Nginx (once, as root)

```bash
# Backend service
cp /home/kfr/app/deploy/kfr-backend.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now kfr-backend
systemctl status kfr-backend

# Nginx site
cp /home/kfr/app/deploy/nginx.conf /etc/nginx/sites-available/kfr
ln -sf /etc/nginx/sites-available/kfr /etc/nginx/sites-enabled/kfr
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```

## SSL certificate (free, from Let's Encrypt)

```bash
certbot --nginx -d keralafirstresponder.org -d www.keralafirstresponder.org
```

Follow the prompts (enter your email, agree to ToS, choose to redirect HTTP → HTTPS).

Your site is now live at **https://keralafirstresponder.org** 🎉

## Default admin login

- Email: `admin@kfr.org`
- Password: `Kfr@2026`

**Change this immediately** by logging in and updating in the DB (or write a small script — ping the dev if you need help).

## Adding email later (when ready)

1. Sign up at [resend.com](https://resend.com)
2. In Resend → Domains → Add `keralafirstresponder.org` → copy the DKIM / SPF / DMARC TXT records
3. In Hostinger DNS Zone, add those 3 TXT records → wait ~10 min → verify in Resend
4. In Resend → API Keys → create one → copy the `re_xxx` key
5. On the VPS:
   ```bash
   nano /home/kfr/app/backend/.env
   # set: RESEND_API_KEY="re_xxx"
   sudo systemctl restart kfr-backend
   ```

Done — every "Generate Test" click now sends real emails.

## Redeploying after code changes

```bash
su - kfr
cd ~/app
bash deploy/deploy.sh    # pulls latest git, rebuilds frontend, restarts backend
```

## Backups

Enable **Hostinger weekly backups** in hPanel (₹79/mo). Also useful:

```bash
# Manual MongoDB dump (run weekly via cron)
mongodump --db kfr_prod --out /root/backups/$(date +%F)
```

## Monitoring

```bash
systemctl status kfr-backend            # service state
tail -f /var/log/kfr-backend.log        # backend logs
tail -f /var/log/nginx/access.log       # nginx traffic
tail -f /var/log/mongodb/mongod.log     # mongo
```
