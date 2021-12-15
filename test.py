#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import logging
import time
from libz import epd2in13_V2
from libz import gt1151
from PIL import Image, ImageDraw, ImageFont

picdir = 'images'  # Points to pic directory
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')

logging.basicConfig(level=logging.DEBUG)
flag_t = 1

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

    # Drawing on the image
    font15 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 15)
    font24 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 24)

    image = Image.open(os.path.join(picdir, 'Menu.bmp'))
    epd.displayPartBaseImage(epd.getbuffer(image))
    DrawImage = ImageDraw.Draw(image)
    epd.init(epd.PART_UPDATE)

logging.info("draw")
DrawImage.text((0, 0), 'Quoth the Raven “Nevermore.”', font=font15, fill=0, align='left')


time.sleep(2)
