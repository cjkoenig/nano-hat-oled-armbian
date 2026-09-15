# NanoHAT OLED for Armbian - Python3
NanoHAT OLED and GPIO Button Control for Armbian. This documentation contains installation and upgrade instructions.

## Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

## Getting Started

### Prerequisites

This guide assumes you are using Armbian Bookworm or newer. `oled-start3.py` in this fork targets the libgpiod v2 Python API (`gpiod.Chip.request_lines()` / `LineSettings`), as shipped with `python3-libgpiod` on Debian Trixie / current Armbian images (e.g. tested on a NanoPi NEO2 running kernel 6.18). If your image still ships libgpiod 1.x (older Bookworm builds), use the upstream script instead, which relies on the older `Chip.get_line()` API.

Enable i2c0:
```
sudo nano /boot/armbianEnv.txt
```
Add `i2c0` to the `overlays=` line, for example if the line appears as follows:
```
overlays=usbhost1 usbhost2
```
Then add `i2c0` with a space seperating it from the other values:
```
overlays=i2c0 usbhost1 usbhost2
```
Save these changes by pressing `ctrl+x`, `ctrl+y` and `enter` as prompted at the bottom of the screen.  
    
Reboot the system for the changes to take effect:
```
sudo reboot now
```

### Dependencies
Install the dependences from APT:
```
sudo apt -y install \
  git \
  python3 \
  python3-libgpiod \
  python3-pil \
  python3-smbus \
  fonts-dejavu-mono
```
`ttf-dejavu` was dropped from Debian; `fonts-dejavu-mono` is the current package providing `DejaVuSansMono.ttf` on Trixie.

### Get the Code
Clone from GitHub:
```
cd /tmp
git clone https://github.com/crouchingtigerhiddenadam/nano-hat-oled-armbian
```

Run the code (optional):
```
cd /tmp/nano-hat-oled-armbian
python3 oled-start3.py
```
Use `ctrl+c` to terminate.

### Install
Make the program directory:
```
sudo mkdir /usr/share/nanohatoled
```
Copy the program files:
```
sudo mv /tmp/nano-hat-oled-armbian/oled-start3.py /usr/share/nanohatoled/
sudo cp /tmp/nano-hat-oled-armbian/splash.png /usr/share/nanohatoled/
```
Compile the code:
```
python3 -O -m py_compile oled-start3.py
```
Install and enable the systemd service:
```
sudo tee /etc/systemd/system/nanohatoled.service > /dev/null <<'EOF'
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
sudo systemctl daemon-reload
sudo systemctl enable --now nanohatoled.service
```
Note: this fork installs autostart via a systemd unit instead of `/etc/rc.local`, since `rc-local.service` isn't reliably enabled on current Armbian (Debian Trixie). If you're upgrading from a previous install that used the `rc.local` method, remove the `cd /usr/share/nanohatoled && ...` line from `/etc/rc.local` to avoid starting the program twice.

## Upgrade from Previous Versions
Get the latest code:
```
cd /tmp
git clone https://github.com/crouchingtigerhiddenadam/nano-hat-oled-armbian
```
Compile the code:
```
cd /tmp/nano-hat-oled-armbian
python3 -O -m py_compile oled-start3.py
```
Remove files from the previous version:
```
sudo rm /usr/share/nanohatoled/* -r
```
Copy the lastest version into place:
```
sudo mv /tmp/nano-hat-oled-armbian/oled-start3.py /usr/share/nanohatoled/
sudo mv /tmp/nano-hat-oled-armbian/splash.png /usr/share/nanohatoled/
```
Compile the code:
```
cd /tmp/nano-hat-oled-armbian
python3 -O -m py_compile oled-start3.py
```
Restart the service to pick up the new version:
```
sudo systemctl restart nanohatoled.service
```
(If you're upgrading from an install that predates the systemd unit, follow the systemd setup steps in the Install section above once, then use `systemctl restart` from then on.)

## Troubleshooting

### Compatibility with BakeBit and NanoHatOLED
This does not require the FriendlyARM BakeBit or NanoHatOLED software to be installed. If this has already been installed you will need disable it.
```
sudo nano /etc/rc.local
```
Then find the lines:
```
/usr/local/bin/oled-start
exit 0
```
And comment out the `oled-start` line by adding `#` at the start of the line, so the lines look like this:
```
# /usr/local/bin/oled-start
exit 0
```
Save these changes by pressing `ctrl+x`, `ctrl+y` and `enter` as prompted at the bottom of the screen.   
   
Reboot the system for the changes to take effect.
```
sudo reboot now
```

## Appendix

### Experimental Quick Install and Update
   
Enable the i2c0 by changing `/boot/armbianEnv.txt` and reboot.   
   
After reboot, run the following command:
```
sudo wget -O - \
  https://raw.githubusercontent.com/crouchingtigerhiddenadam/nano-hat-oled-armbian/primary/install3.sh | \
  sudo bash -
```
The command can be used to make a fresh installation or update an existing installation to the latest version.
   
Reboot the system for the changes to take effect:
```
sudo reboot now
```
