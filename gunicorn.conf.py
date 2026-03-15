# ── Entertainment Hub - Gunicorn Configuration ──────────────────────────

# Server socket
bind = "127.0.0.1:5000"

# Workers: (2 × CPU cores) + 1  is the recommended formula
workers = 3

# Worker class
worker_class = "sync"

# Timeout (seconds) — increase if uploads are slow
timeout = 120

# Logging
accesslog = "/var/log/entertainmenthub/access.log"
errorlog = "/var/log/entertainmenthub/error.log"
loglevel = "info"

# Process naming
proc_name = "entertainmenthub"

# Security
limit_request_line = 8190
limit_request_fields = 100
