#!/bin/bash
# ── Entertainment Hub - Production Deployment Script ──────────────────
# Run this script on your Linux server to set up the application.
# Usage: chmod +x deploy.sh && sudo ./deploy.sh

set -e  # Exit on any error

# ─── Configuration (EDIT THESE) ──────────────────────────────────────
APP_NAME="entertainmenthub"
APP_USER="entertainmenthub"
APP_DIR="/opt/entertainmenthub"
DOMAIN="ehub.subhashguptha.online"    # Your subdomain

# ─── Colors ──────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Entertainment Hub — Production Deployment"
echo "════════════════════════════════════════════════════════════"
echo ""

# ─── Step 1: System Packages ────────────────────────────────────────
log "Installing system packages..."
apt update -qq
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx ufw sqlite3

# ─── Step 2: Create App User ────────────────────────────────────────
if ! id "$APP_USER" &>/dev/null; then
    log "Creating system user: $APP_USER"
    useradd -r -m -d "$APP_DIR" -s /bin/bash "$APP_USER"
else
    log "User $APP_USER already exists"
fi

# ─── Step 3: Copy App Files ─────────────────────────────────────────
log "Setting up application directory: $APP_DIR"
mkdir -p "$APP_DIR"

# Copy project files (run from the project directory)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp -r "$SCRIPT_DIR/app.py" "$APP_DIR/"
cp -r "$SCRIPT_DIR/database.py" "$APP_DIR/"
cp -r "$SCRIPT_DIR/requirements.txt" "$APP_DIR/"
cp -r "$SCRIPT_DIR/gunicorn.conf.py" "$APP_DIR/"
cp -r "$SCRIPT_DIR/static" "$APP_DIR/"
cp -r "$SCRIPT_DIR/templates" "$APP_DIR/"

# Copy database only if it doesn't exist on server (preserve existing data)
if [ ! -f "$APP_DIR/entertainmenthub.db" ]; then
    cp "$SCRIPT_DIR/entertainmenthub.db" "$APP_DIR/"
    log "Database copied (fresh install)"
else
    warn "Database already exists on server — skipping copy to preserve data"
fi

chown -R "$APP_USER:$APP_USER" "$APP_DIR"

# ─── Step 4: Python Virtual Environment ─────────────────────────────
log "Setting up Python virtual environment..."
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/venv"
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --upgrade pip -q
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt" -q
log "Dependencies installed"

# ─── Step 5: Generate Secret Key ────────────────────────────────────
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
log "Generated secure SECRET_KEY"

# ─── Step 6: Create Log Directory ───────────────────────────────────
mkdir -p /var/log/entertainmenthub
chown "$APP_USER:$APP_USER" /var/log/entertainmenthub

# ─── Step 7: Systemd Service ────────────────────────────────────────
log "Creating systemd service..."

cat > /etc/systemd/system/${APP_NAME}.service << EOF
[Unit]
Description=Entertainment Hub - OTT Streaming Platform
After=network.target
Wants=network-online.target

[Service]
Type=notify
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin:/usr/bin"
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=${SECRET_KEY}"
ExecStart=${APP_DIR}/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5
StartLimitBurst=5
StartLimitIntervalSec=60
StandardOutput=journal
StandardError=journal

# Security hardening
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=${APP_DIR} /var/log/entertainmenthub

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$APP_NAME"
log "Systemd service created and enabled"

# ─── Step 8: Nginx Reverse Proxy ────────────────────────────────────
log "Configuring Nginx..."

cat > /etc/nginx/sites-available/${APP_NAME} << 'NGINX_EOF'
# Entertainment Hub - Nginx Configuration
# Rate limiting zone
limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Max upload size (for image uploads)
    client_max_body_size 10M;

    # Static files - served directly by Nginx (much faster)
    location /static/ {
        alias APP_DIR_PLACEHOLDER/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;

        # Gzip compression for text assets
        gzip on;
        gzip_types text/css application/javascript text/javascript image/svg+xml;
        gzip_min_length 1000;
    }

    # Image files
    location /images/ {
        alias APP_DIR_PLACEHOLDER/static/images/;
        expires 30d;
        add_header Cache-Control "public";
        access_log off;
    }

    # API routes - rate limited
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    # All other routes (HTML pages)
    location / {
        limit_req zone=general burst=50 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_EOF

# Replace placeholders with actual values
sed -i "s|DOMAIN_PLACEHOLDER|${DOMAIN}|g" /etc/nginx/sites-available/${APP_NAME}
sed -i "s|APP_DIR_PLACEHOLDER|${APP_DIR}|g" /etc/nginx/sites-available/${APP_NAME}

# Enable site
ln -sf /etc/nginx/sites-available/${APP_NAME} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default  # Remove default Nginx page

nginx -t || err "Nginx config test failed!"
log "Nginx configured"

# ─── Step 9: Firewall ───────────────────────────────────────────────
log "Configuring firewall..."
ufw allow 22/tcp     # SSH
ufw allow 80/tcp     # HTTP
ufw allow 443/tcp    # HTTPS
ufw --force enable
log "Firewall active (SSH, HTTP, HTTPS allowed)"

# ─── Step 10: Database Permissions ──────────────────────────────────
chmod 664 "$APP_DIR/entertainmenthub.db"
chown "$APP_USER:$APP_USER" "$APP_DIR/entertainmenthub.db"
log "Database permissions set"

# ─── Step 11: Start Everything ──────────────────────────────────────
log "Starting services..."
systemctl start "$APP_NAME"
systemctl restart nginx

# ─── Step 12: Verify ────────────────────────────────────────────────
sleep 2
if systemctl is-active --quiet "$APP_NAME"; then
    log "Entertainment Hub is RUNNING!"
else
    err "Service failed to start. Check: journalctl -u $APP_NAME -n 50"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ DEPLOYMENT COMPLETE!"
echo ""
echo "  🌐 Website:     http://${DOMAIN}"
echo "  🔧 Admin Panel: http://${DOMAIN}/admin/index.html"
echo ""
echo "  📋 Useful commands:"
echo "     sudo systemctl status ${APP_NAME}     # Check status"
echo "     sudo systemctl restart ${APP_NAME}    # Restart app"
echo "     sudo journalctl -u ${APP_NAME} -f     # Live logs"
echo ""
echo "  🔒 To add HTTPS (strongly recommended):"
echo "     sudo certbot --nginx -d ${DOMAIN}"
echo ""
echo "  💾 SECRET_KEY has been auto-generated and stored in"
echo "     the systemd service file."
echo "════════════════════════════════════════════════════════════"
echo ""
