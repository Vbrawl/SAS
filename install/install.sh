
WEBSITE_DIR="/var/www/sas"
DAEMON_DIR="/opt/SAS"
PYTHON_EXE="/bin/python"
SERVICE_DIR="/etc/systemd/system"

DAEMON_SOURCE="../src/sas_daemon"
WEBSITE_SOURCE="../src/sas_control_panel"

# Create directories
mkdir -p $WEBSITE_DIR
mkdir -p $DAEMON_DIR

# Copy website
cp -R $WEBSITE_SOURCE/src/* $WEBSITE_DIR

# Create virtual environment directory
$PYTHON_EXE -m venv "${DAEMON_DIR}/.venv"

# Load virtual environment and install sas_daemon inside of it
source "${DAEMON_DIR}/.venv/bin/activate"
pip install $DAEMON_SOURCE

# Create the service file
cat > "${SERVICE_DIR}/sasd.service" << EOF
[Unit]
Description=Send Automated SMS
After=network.target

[Service]
WorkingDirectory=$DAEMON_DIR
ExecStart=${DAEMON_DIR}/.venv/bin/sas-daemon

[Install]
WantedBy=multi-user.target
EOF

# Reload daemons and enable service
systemctl daemon-reload
systemctl enable --now sasd.service