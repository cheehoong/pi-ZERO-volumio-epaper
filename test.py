#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import logging
import time
from libz import epd2in13_V2
from libz import gt1151
from PIL import Image, ImageDraw, ImageFont

picdir = 'images'  # Points to pic directory

logging.basicConfig(level=logging.DEBUG)
flag_t = 1

logging.info("clear the frame")
image = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame

logging.info("Start initial")
try:
    logging.info("epd2in13_V2 Touch Demo")

    epd = epd2in13_V2.EPD_2IN13_V2()
    gt = gt1151.GT1151()
    GT_Dev = gt1151.GT_Development()
    GT_Old = gt1151.GT_Development()

    logging.info("init and Clear")
    epd.init(epd.FULL_UPDATE)
    gt.GT_Init()
    epd.Clear(0xFF)

except IOError as e:
    print(e)

logging.info("draw")
draw = ImageDraw.Draw(image)
draw.rectangle((0, 10, 200, 34), fill=1)
draw.line((1, 60, 56, 60), fill=0)
draw.line((56, 60, 56, 110), fill=0)
draw.line((16, 110, 56, 110), fill=1)
draw.line((16, 110, 16, 60), fill=0)
draw.line((16, 60, 56, 110), fill=0)
draw.line((56, 60, 16, 110), fill=0)
draw.arc((90, 60, 150, 120), 0, 360, fill=0)
draw.rectangle((16, 130, 56, 180), fill=0)
draw.chord((90, 130, 150, 190), 0, 360, fill=0)
time.sleep(2)
