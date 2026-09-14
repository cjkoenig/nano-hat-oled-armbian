#!/usr/bin/env python3

import time
import os
import subprocess
import smbus
import gpiod
from gpiod.line import Direction, Bias

from PIL import Image, ImageDraw, ImageFont

I2C_ADDR = 0x3C
I2C_BUS = 0
DISPLAY_TIMEOUT = 30

# ---------- I2C / OLED ----------
bus = smbus.SMBus(I2C_BUS)

def oled_cmd(cmds):
    bus.write_i2c_block_data(I2C_ADDR, 0x00, cmds)

def oled_data(data):
    for i in range(0, len(data), 32):
        bus.write_i2c_block_data(I2C_ADDR, 0x40, data[i:i+32])

def oled_init():
    oled_cmd([
        0xAE, 0x20, 0x00, 0x40,
        0xA1, 0xC8, 0x81, 0xCF,
        0xA8, 0x3F, 0xD3, 0x00,
        0xD5, 0x80, 0xD9, 0xF1,
        0xDA, 0x12, 0xDB, 0x40,
        0x8D, 0x14, 0xA6, 0xAF
    ])

def oled_off():
    oled_cmd([0xAE])

def oled_on():
    oled_cmd([0xAF])

def draw_image(img):
    pixels = img.load()
    buf = []

    for page in range(8):
        for x in range(128):
            byte = 0
            for bit in range(8):
                byte |= (pixels[x, page*8 + bit] << (7-bit))
            buf.append(byte)

    oled_data(buf)

# ---------- Fonts ----------
font10 = ImageFont.truetype("DejaVuSansMono.ttf", 10)
font15 = ImageFont.truetype("DejaVuSansMono.ttf", 15)

# ---------- Image ----------
img = Image.new("1", (128, 64))
draw = ImageDraw.Draw(img)

# ---------- GPIO (libgpiod v2) ----------
chip = gpiod.Chip("/dev/gpiochip0")

lines = chip.request_lines(
    consumer="oled-buttons",
    config={
        0: gpiod.LineSettings(direction=Direction.INPUT, bias=Bias.PULL_UP),
        2: gpiod.LineSettings(direction=Direction.INPUT, bias=Bias.PULL_UP),
        3: gpiod.LineSettings(direction=Direction.INPUT, bias=Bias.PULL_UP),
    },
)

def read_buttons():
    vals = lines.get_values([0, 2, 3])
    return (not vals[0], not vals[1], not vals[2])  # invert wegen pull-up

# ---------- System Infos ----------
def get_ip():
    try:
        return subprocess.check_output(
            "hostname -I | awk '{print $1}'",
            shell=True, text=True).strip()
    except:
        return "no IP"

def get_stats():
    try:
        load = subprocess.check_output(
            "cut -d ' ' -f1 /proc/loadavg",
            shell=True, text=True).strip()
        temp = int(open("/sys/class/thermal/thermal_zone0/temp").read()) / 1000
        return f"Load:{load} Temp:{temp:.1f}C"
    except:
        return "stats error"

# ---------- Display States ----------
state = 0
last_refresh = 0
display_off_time = time.time() + DISPLAY_TIMEOUT

oled_init()

try:
    while True:
        time.sleep(0.1)
        now = time.time()

        b1, b2, b3 = read_buttons()

        if b1:
            state = 0
            display_off_time = now + DISPLAY_TIMEOUT

        elif b2:
            state = 1
            display_off_time = now + DISPLAY_TIMEOUT

        if now > display_off_time:
            oled_off()
            continue
        else:
            oled_on()

        if now - last_refresh < 1:
            continue

        draw.rectangle((0, 0, 128, 64), 0)

        if state == 0:
            draw.text((0, 0), time.strftime("%H:%M:%S"), font=font15, fill=1)
            draw.text((0, 20), time.strftime("%d.%m.%Y"), font=font10, fill=1)

        elif state == 1:
            draw.text((0, 0), f"IP: {get_ip()}", font=font10, fill=1)
            draw.text((0, 15), get_stats(), font=font10, fill=1)

        draw_image(img)
        last_refresh = now

except KeyboardInterrupt:
    pass

finally:
    oled_off()
    lines.release()
    chip.close()