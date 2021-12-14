#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys
import time
import requests
import logging
from PIL import Image, ImageDraw, ImageFont
from . import epd2in13_V2
from . import gt1151
from TP2in13_test import picdir
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib')))
font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)

logging.basicConfig(level=logging.DEBUG)
flag_t = 1

logging.info("1")
response2 = requests.get("http://volumio0.local:3000/api/v1/getState")
r2 = response2.json()

logging.info("epd2in13_V2 Touch Demo")
epd = epd2in13_V2.EPD_2IN13_V2()
gt = gt1151.GT1151()
GT_Dev = gt1151.GT_Development()
GT_Old = gt1151.GT_Development()

logging.info("clear the frame")
image = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame

logging.info("draw")
draw = ImageDraw.Draw(image)
draw.rectangle((0, 10, 200, 34), fill=0)
draw.text((8, 12), r2['title'], font=font, fill=255)
draw.text((8, 24), 'hello world', font=font, fill=255)
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
