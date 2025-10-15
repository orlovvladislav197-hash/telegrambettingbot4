VPS Deployment Guide (Ubuntu 22.04+)

1) Create VPS (DigitalOcean/Hetzner/OVH/AWS).

2) SSH and update:
sudo apt update && sudo apt upgrade -y

3) Install Docker:
# see full commands in previous instructions (use Docker official repo).

4) Upload project, create .env (we included .env), edit TELEGRAM_TOKEN and RPC_URL.

5) Start services:
docker compose up -d --build

6) Init DB:
docker compose exec db psql -U botuser -d betting -f db/init.sql

7) Configure nginx and certbot, see nginx.conf included.

8) Create systemd unit for autostart if needed.
