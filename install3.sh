#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please re-run as root user."
  exit
fi

# Get dependencies from APT
apt -y install \
  git \
  python3 \
  python3-libgpiod \
  python3-pil \
  python3-smbus \
  fonts-dejavu-mono

# Get the code
if [ -d "/tmp/nano-hat-oled-armbian" ]
then
  rm /tmp/nano-hat-oled-armbian -rf
fi
cd /tmp
git clone https://github.com/crouchingtigerhiddenadam/nano-hat-oled-armbian
cd ./nano-hat-oled-armbian

# Setup systemd unit
tee /etc/systemd/system/nanohatoled.service > /dev/null <<'EOF'
[Unit]
Description=NanoHAT OLED Display and Button Control
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=/usr/share/nanohatoled
ExecStart=/usr/bin/python3 /usr/share/nanohatoled/oled-start3.py
Restart=on-failure
Nice=10

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload

# Make the program directory
if [ ! -d "/usr/share/nanohatoled" ]
then
  mkdir /usr/share/nanohatoled
fi

# Copy program files
mv oled-start3.py /usr/share/nanohatoled/
mv splash.png /usr/share/nanohatoled/

# Move to directory
cd /usr/share/nanohatoled/

# Compile the code
python3 -O -m py_compile oled-start3.py

# Start OLED
systemctl enable --now nanohatoled.service
