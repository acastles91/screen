#!/usr/bin/python3
# SPDX-FileCopyrightText: 2025 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
Display quote from the Adafruit quotes API as text scrolling across the
matrices.

Requires the requests library to be installed.

Run like this:

$ python quote_scroller.py

"""

import time
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont

import adafruit_blinka_raspberry_pi5_piomatter as piomatter



import re
import time
import random
from pathlib import Path

i# ---------- settings ----------
VAULT_PATH = Path("/home/antonio/vault/LED")  # a folder of .md files OR a single .md file
SHUFFLE = False                               # True = random order each pass
SPEED = 100                                   # pixels per second
total_width = 256
total_height = 64
bottom_half_shift_compensation = -1
font_color = (255, 255, 0)
font = ImageFont.truetype("LindenHill-webfont.ttf", 48)
# ------------------------------

half = total_height // 2
shift = bottom_half_shift_compensation

def clean(line):
    line = re.sub(r"^\s*(#{1,6}\s+|[-*+]\s+(\[.\]\s+)?|>\s*|\d+\.\s+)", "", line)  # headings, bullets, checkboxes, quotes
    line = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]", r"\1", line)                  # [[link|alias]] -> alias
    line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)                            # [text](url) -> text
    line = re.sub(r"%%.*?%%", "", line)                                             # obsidian comments
    line = re.sub(r"[*`~]+", "", line)                                              # bold/italic/code marks
    return line.strip()


def load_messages():
    if VAULT_PATH.is_file():
        files = [VAULT_PATH]
    elif VAULT_PATH.is_dir():
        files = sorted(VAULT_PATH.rglob("*.md"))
    else:
        return [f"Path not found: {VAULT_PATH}"]

    msgs = []
    for f in files:
        try:
            t = f.read_text(encoding="utf-8")
        except OSError:
            continue
        t = re.sub(r"\A---\n.*?\n---\n", "", t, flags=re.S)  # frontmatter
        t = re.sub(r"```.*?```", "", t, flags=re.S)           # code blocks
        for line in t.splitlines():
            line = clean(line)
            if line:
                msgs.append(line)
    return msgs or ["No messages found"]


def render(text):
    ascent, descent = font.getmetrics()
    y = (total_height - (ascent + descent)) // 2   # same baseline for every message
    img = Image.new("RGB", (int(font.getlength(text)) + 8, total_height), (0, 0, 0))
    ImageDraw.Draw(img).text((3, y), text, font=font, fill=font_color)
    return img


# ---------- matrix setup ----------
single_frame_img = Image.new("RGB", (total_width, total_height), (0, 0, 0))
geometry = piomatter.Geometry(width=total_width, height=total_height,
                              n_addr_lines=5, n_planes=10, n_temporal_planes=4,
                              rotation=piomatter.Orientation.R180)
framebuffer = np.asarray(single_frame_img) + 0
matrix = piomatter.PioMatter(colorspace=piomatter.Colorspace.RGB888Packed,
                             pinout=piomatter.Pinout.AdafruitMatrixBonnet,
                             framebuffer=framebuffer,
                             geometry=geometry)


def scroll(img):
    """Scroll one message across the display once."""
    cycle = img.width + total_width + 1
    start = time.monotonic()
    while True:
        offset = int((time.monotonic() - start) * SPEED)
        if offset >= cycle:
            return
        x = offset - total_width - 1

        single_frame_img.paste(
            img.crop((x, 0, x + total_width, half)), (0, 0))
        single_frame_img.paste(
            img.crop((x - shift, half, x - shift + total_width, total_height)), (0, half))

        framebuffer[:] = np.asarray(single_frame_img)
        matrix.show()
        time.sleep(1 / 60)


print("Ctrl-C to exit")
while True:
    messages = load_messages()
    if SHUFFLE:
        random.shuffle(messages)
    for msg in messages:
        scroll(render(msg))

'''





# 128px for 2x1 matrices. Change to 64 if you're using a single matrix.
total_width = 256
total_height = 64

bottom_half_shift_compensation = -2

font_color = (255, 255, 0)

# Load the font
font = ImageFont.truetype("LindenHill-webfont.ttf", 48)

quote_resp = requests.get("https://www.adafruit.com/api/quotes.php").json()

text = f'{quote_resp[0]["text"]} - {quote_resp[0]["author"]}'
#text = "Sometimes you just want to use hardcoded strings. - Unknown"

x, y, text_width, text_height = font.getbbox(text)
left, top, right, bottom = font.getbbox(text)

y = (total_height - (bottom - top)) // 2 - top

#full_txt_img = Image.new("RGB", (int(text_width) + 6, int(text_height) + 6), (0, 0, 0))
full_txt_img = Image.new("RGB", (right + 6, total_height), (0, 0, 0))

draw = ImageDraw.Draw(full_txt_img)

#draw.text((3, 3), text, font=font, fill=font_color)
draw.text((3, y), text, font=font, fill=font_color)
full_txt_img.save("quote.png")

single_frame_img = Image.new("RGB", (total_width, total_height), (0, 0, 0))

geometry = piomatter.Geometry(width=total_width, height=total_height,
                              n_addr_lines=5, n_planes=10, n_temporal_planes=4, rotation=piomatter.Orientation.R180)
framebuffer = np.asarray(single_frame_img) + 0  # Make a mutable copy

matrix = piomatter.PioMatter(colorspace=piomatter.Colorspace.RGB888Packed,
                             pinout=piomatter.Pinout.AdafruitMatrixBonnet,
                             framebuffer=framebuffer,
                             geometry=geometry)

print("Ctrl-C to exit")

speed = 80
half = total_height // 2
shift = bottom_half_shift_compensation
cycle = full_txt_img.width + total_width + 1

start = time.monotonic()


while True:
    x_pixel = int((time.monotonic() - start) * speed) % cycle - total_width - 1 '''
    '''for x_pixel in range(-total_width-1,full_txt_img.width):
        if bottom_half_shift_compensation == 0:
            # full paste
            single_frame_img.paste(full_txt_img.crop((x_pixel, 0, x_pixel + total_width, total_height)), (0, 0))

        else:
            # top half
            single_frame_img.paste(full_txt_img.crop((x_pixel, 0, x_pixel + total_width, total_height//2)), (0, 0))
            # bottom half shift compensation
            single_frame_img.paste(full_txt_img.crop((x_pixel, total_height//2, x_pixel + total_width, total_height)), (bottom_half_shift_compensation, total_height//2))

        framebuffer[:] = np.asarray(single_frame_img)
        matrix.show()


    single_frame_img.paste(
        full_txt_img.crop((x_pixel, 0, x_pixel + total_width, half)), (0, 0))
    # bottom half, shifted by `shift` pixels
    single_frame_img.paste(
        full_txt_img.crop((x_pixel - shift, half,
                           x_pixel - shift + total_width, total_height)), (0, half))

    framebuffer[:] = np.asarray(single_frame_img)
    matrix.show()
    #time.sleep(1 / 60)
'''