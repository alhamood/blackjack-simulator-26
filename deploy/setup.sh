#!/bin/bash
# Blackjack Simulator - Server Setup Script
# Run on a fresh Ubuntu 22.04 Lightsail instance
#
# Usage:
#   scp deploy/setup.sh ubuntu@<your-ip>:~/setup.sh
#   ssh ubuntu@<your-ip>
#   chmod +x setup.sh && sudo ./setup.sh

set -euo pipefail

REPO_URL="https://github.com/alhamood/blackjack-simulator-26.git"
APP_DIR="/opt/blackjack"
DOMAIN="blackjack.hamood.com"

echo "=== Blackjack Simulator Server Setup ==="

# 1. System packages
echo "[1/6] Installing system packages..."
apt update -qq
apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx git

# 2. Clone repo
echo "[2/6] Cloning repository..."
if [ -d "$APP_DIR" ]; then
    echo "  $APP_DIR exists, pulling latest..."
    cd "$APP_DIR" && git pull
else
    git clone "$REPO_URL" "$APP_DIR"
fi
chown -R ubuntu:ubuntu "$APP_DIR"

# 3. Python venv + dependencies
echo "[3/6] Setting up Python environment..."
cd "$APP_DIR"
sudo -u ubuntu python3 -m venv venv
sudo -u ubuntu venv/bin/pip install --quiet -r requirements.txt

# 4. Systemd service
echo "[4/6] Installing systemd service..."
cp deploy/blackjack.service /etc/systemd/system/blackjack.service
systemctl daemon-reload
systemctl enable blackjack
systemctl restart blackjack

echo "  Waiting for app to start..."
sleep 3
if systemctl is-active --quiet blackjack; then
    echo "  App is running!"
else
    echo "  WARNING: App failed to start. Check: journalctl -u blackjack"
fi

# 5. Nginx config
echo "[5/6] Configuring nginx..."
cp deploy/blackjack-nginx.conf /etc/nginx/sites-available/blackjack
ln -sf /etc/nginx/sites-available/blackjack /etc/nginx/sites-enabled/blackjack
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 6. SSL (run manually after DNS is pointed)
echo "[6/6] SSL setup..."
echo ""
echo "  DNS must be pointing to this server before SSL setup."
echo "  Once DNS is ready, run:"
echo ""
echo "    sudo certbot --nginx -d $DOMAIN"
echo ""

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Point $DOMAIN A record to this server's IP"
echo "  2. Run: sudo certbot --nginx -d $DOMAIN"
echo "  3. Visit https://$DOMAIN"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status blackjack    # Check app status"
echo "  sudo journalctl -u blackjack -f    # View app logs"
echo "  cd $APP_DIR && git pull && sudo systemctl restart blackjack  # Deploy updates"
echo ""
