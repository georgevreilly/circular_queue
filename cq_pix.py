#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont

import math
import os


def wedge_start_angle(i, n):
    return (360 + -90 + i * (360 // n)) % 360


def point(degrees, radius):
    rads = math.radians(degrees)
    x, y = round(radius * math.cos(rads)), round(radius * math.sin(rads))
    return x, y


def render_circular_buffer(values, fnt, filename=None, width=300, height=300, read=None, write=None, multiplier=2):
    width *= multiplier
    height *= multiplier
    CX = int(width / 2)
    CY = int(height / 2)

    X0 = int(width / 6)
    X1 = width - X0
    Y0 = int(height / 6)
    Y1 = height - Y0

    BBOX1 = [(X0, Y0), (X1, Y1)]

    im = Image.new("RGB", (width, height), "#F5E1D2")
    draw = ImageDraw.Draw(im)
    N = len(values)
    delta = 360 // N
    text_radius = round(width * 0.27)

    draw.arc([(X0-multiplier, Y0-multiplier), (X1+multiplier, Y1+multiplier)], 0, 360, fill="black", width=multiplier * 42)

    for i, v in enumerate(values):
        text = str(v or 'X')
        wedge_start = wedge_start_angle(i, N)
        text_degrees = wedge_start + delta / 2
        wedge_end = wedge_start + delta
        sat = 208 if v else 160
        if i % 2 == 0:
            fill = (sat, 0, 0) # red
            text_color = "#01ACAD"
        else:
            fill = (sat, sat, 0) # yellow
            text_color = "#BD7CB4"
        draw.arc(BBOX1, wedge_start, wedge_end, fill=fill, width=multiplier * 40)

        x, y = point(text_degrees, text_radius)
        shadow = "#000"
        draw.text((CX + x + 1, CY + y + 1), text, fill=shadow, font=fnt, anchor="mm")
        draw.text((CX + x + 0, CY + y + 0), text, fill=text_color, font=fnt, anchor="mm")

        for angle_offset, fill, state in [
                (12, (16*i+80, 0, 0), "r"),
                (delta - 12, (0, 16*i+80, 0), "w"),
            ]:
            if state == "r" and read == i or state == "w" and write == i:
                d = wedge_start + angle_offset
                x0, y0 = point(d, text_radius+ multiplier * 40)
                x1, y1 = point(d+3, text_radius+ multiplier * 66)
                x2, y2 = point(d-3, text_radius+ multiplier * 66)
                for ofs, color in [(multiplier, "black"), (0, fill)]:
                    triangle = [
                        (CX + x0 + ofs, CY + y0 + ofs),
                        (CX + x1 + ofs, CY + y1 + ofs),
                        (CX + x2 + ofs, CY + y2 + ofs),
                    ]
                    draw.polygon(triangle, fill=color)

    im = im.resize((width // multiplier, height // multiplier), Image.ANTIALIAS)
    if filename:
        im.save(filename)
    else:
        im.show()


FONT_DIR = '/Users/georgevreilly/tmp/fonts/'
FONTSIZE = 24
MULTIPLIER = 5

fontfile = os.path.join(FONT_DIR, 'FiraFonts4106/OTF/FiraSans-SemiBold.otf')
fnt = ImageFont.truetype(fontfile, size=MULTIPLIER * FONTSIZE)

values = [None, None, 32, 33, 34, 35, None, None, None, None]
render_circular_buffer(values, fnt=fnt, read=2, write=6, multiplier=MULTIPLIER)
