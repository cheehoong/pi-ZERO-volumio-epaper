#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys
import time

import easygui
import requests

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic/2in13')
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from python.lib import gt1151
from python.lib import epd2in13_V2
from PIL import Image, ImageDraw, ImageFont

easygui.msgbox('title', title="simple gui")
response2 = requests.get("http://volumio0.local:3000/api/v1/getState")
r2 = response2.json()
easygui.msgbox(r2['title'], title="simple gui")

epd = epd2in13_V2.EPD_2IN13_V2()
gt = gt1151.GT1151()
GT_Dev = gt1151.GT_Development()
GT_Old = gt1151.GT_Development()

image = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame

draw = ImageDraw.Draw(image)
font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
draw.rectangle((0, 10, 200, 34), fill=0)
draw.text((8, 12), 'hello world', font=font, fill=255)
draw.text((8, 36), u'微雪电子', font=font, fill=0)
draw.line((16, 60, 56, 60), fill=0)
draw.line((56, 60, 56, 110), fill=0)
draw.line((16, 110, 56, 110), fill=0)
draw.line((16, 110, 16, 60), fill=0)
draw.line((16, 60, 56, 110), fill=0)
draw.line((56, 60, 16, 110), fill=0)
draw.arc((90, 60, 150, 120), 0, 360, fill=0)
draw.rectangle((16, 130, 56, 180), fill=0)
draw.chord((90, 130, 150, 190), 0, 360, fill=0)
epd.display(epd.getbuffer(image.rotate(90)))
time.sleep(2)
