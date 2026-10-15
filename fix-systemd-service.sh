#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE_NAME="${SERVICE_NAME:-cantarellabots_bot}"
APP_DIR="${APP_DIR:-/root/CDML-X}"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
DROPIN_DIR="/etc/systemd/system/${SERVICE_NAME}.service.d"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root: sudo bash fix-systemd-service.sh" >&2
  exit 1
fi
if [[ ! -d "$APP_DIR" ]]; then
  echo "ERROR: project directory not found: $APP_DIR" >&2
  exit 1
fi
if [[ ! -f "$APP_DIR/start.sh" ]]; then
  echo "ERROR: startup script not found: $APP_DIR/start.sh" >&2
  exit 1
fi
if [[ ! -x /bin/bash ]]; then
  echo "ERROR: /bin/bash is not executable" >&2
  exit 1
fi

# Normalize the script and make it executable. ExecStart invokes Bash directly,
# so systemd does not depend on the script's shebang or executable bit.
sed -i 's/\r$//' "$APP_DIR/start.sh"
chmod 755 "$APP_DIR/start.sh"

# Override even stale unit files that still try to execute start.sh directly.
mkdir -p "$DROPIN_DIR"
cat > "$DROPIN_DIR/override.conf" <<EOF2
[Service]
ExecStart=
ExecStart=/bin/bash ${APP_DIR}/start.sh
Restart=on-failure
RestartSec=10
StartLimitIntervalSec=0
EOF2

systemctl daemon-reload
systemctl reset-failed "$SERVICE_NAME" || true
systemctl restart "$SERVICE_NAME"
sleep 4
if systemctl is-active --quiet "$SERVICE_NAME"; then
  echo "Service is active: $SERVICE_NAME"
  systemctl status "$SERVICE_NAME" --no-pager -l
else
  echo "Service did not stay active. Recent diagnostics:" >&2
  systemctl show "$SERVICE_NAME" -p ExecStart -p WorkingDirectory -p FragmentPath -p DropInPaths >&2 || true
  systemctl status "$SERVICE_NAME" --no-pager -l >&2 || true
  journalctl -u "$SERVICE_NAME" -n 100 --no-pager >&2 || true
  exit 1
fi
