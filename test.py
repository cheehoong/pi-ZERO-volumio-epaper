#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import logging
import time
from libz import epd2in13_V2
from libz import gt1151
from PIL import Image, ImageDraw, ImageFont
import requests

logging.basicConfig(level=logging.DEBUG)
flag_t = 1

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')  # Points to pic directory
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')

logging.info("Start initial")

logging.info("epd2in13_V2 Touch Demo")
epd = epd2in13_V2.EPD_2IN13_V2()
gt = gt1151.GT1151()
GT_Dev = gt1151.GT_Development()
GT_Old = gt1151.GT_Development()

logging.info("init and Clear")
epd.init(epd.FULL_UPDATE)
gt.GT_Init()
epd.Clear(0xFF)

# Drawing on the image
font15 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 15)
font24 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 24)

image = Image.open(os.path.join(picdir, 'Empty2.bmp'))
epd.displayPartBaseImage(epd.getbuffer(image))
DrawImage = ImageDraw.Draw(image)
epd.init(epd.PART_UPDATE)
# time.sleep(2)


server = "http://localhost:3000/api/v1/getState"
response = requests.get(server)
info = response.json()
print(info['title'])

logging.info("draw")
im = Image.open(os.path.join(picdir, 'Empty2.bmp'))
draw = ImageDraw.Draw(im)
# draw.line((0, 0) + im.size, fill=0)
# draw.line((0, im.size[1], im.size[0], 0), fill=0)
# draw.rectangle((0, 10, 20, 34), fill=0)
# draw.line((16, 60, 56, 60), fill=0)
logging.info("drawline")
draw.text((8, 12), info['title'], font=font15, fill=0)
draw.text((8, 36), 'e-Paper Demo', font=font24, fill=0)
im2 = im.transpose(method=Image.ROTATE_90)
logging.info("before paste")
time.sleep(2)
image.paste(im2, (2, 2))
logging.info("pasted")
time.sleep(2)
epd.displayPartial(epd.getbuffer(im2))
epd.init(epd.PART_UPDATE)

time.sleep(2)

