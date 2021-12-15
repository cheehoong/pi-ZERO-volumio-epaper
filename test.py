#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import logging
import time
from libz import epd2in13_V2
from libz import gt1151
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.DEBUG)
flag_t = 1

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')  # Points to pic directory
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')


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

    image = Image.open(picdir, 'Menu.bmp')
    epd.displayPartBaseImage(epd.getbuffer(image))
    DrawImage = ImageDraw.Draw(image)
    epd.init(epd.PART_UPDATE)

logging.info("draw")
image = Image.new(
    '1',
    (epd1in54.EPD_WIDTH, epd1in54.EPD_HEIGHT),
    255  # 255: clear the frame
)
draw = ImageDraw.Draw(image)
font = ImageFont.truetype(
    '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf',
    24
)
draw.rectangle((0, 10, 200, 34), fill=0)
draw.text((8, 12), 'Hello world!', font=font, fill=255)
draw.text((8, 36), 'e-Paper Demo', font=font, fill=0)
draw.line((16, 60, 56, 60), fill=0)
draw.line((56, 60, 56, 110), fill=0)
draw.line((16, 110, 56, 110), fill=0)
draw.line((16, 110, 16, 60), fill=0)
draw.line((16, 60, 56, 110), fill=0)
draw.line((56, 60, 16, 110), fill=0)
draw.arc((90, 60, 150, 120), 0, 360, fill=0)
draw.rectangle((16, 130, 56, 180), fill=0)
draw.chord((90, 130, 150, 190), 0, 360, fill=0)

epd.clear_frame_memory(0xFF)
epd.set_frame_memory(image, 0, 0)
epd.display_frame()


time.sleep(2)
