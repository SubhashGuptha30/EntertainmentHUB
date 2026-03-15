#!/bin/bash
# ── Entertainment Hub - Automated Backup Script ──────────────────────
# Schedule this with cron: 0 3 * * * /opt/entertainmenthub/backup.sh
# This runs daily at 3:00 AM

APP_DIR="/opt/entertainmenthub"
BACKUP_DIR="/opt/entertainmenthub/backups"
MAX_BACKUPS=14  # Keep last 14 days

mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/db_backup_${TIMESTAMP}.db"

# Use SQLite's online backup (safe even while app is running)
sqlite3 "$APP_DIR/entertainmenthub.db" ".backup '$BACKUP_FILE'"

# Compress
gzip "$BACKUP_FILE"

# Cleanup old backups (keep only last N)
ls -t "$BACKUP_DIR"/db_backup_*.db.gz 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm

echo "[$(date)] Backup created: ${BACKUP_FILE}.gz"
