#!/usr/bin/python
# -*- coding:utf-8 -*-
import argparse
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

def clear_display(display):
    logging.info('Clearing display...')
    epd.Clear(0xFF)

def parse_args():
    p = argparse.ArgumentParser(description='Test EPD functionality')
    p.add_argument('-v', '--virtual', action='store_true',
                   help='display using a Tkinter window instead of the '
                        'actual e-paper device (for testing without a '
                        'physical device)')
    p.add_argument('-r', '--rotate', default=None, choices=['CW', 'CCW', 'flip'],
                   help='run the tests with the display rotated by the specified value')
    p.add_argument('-e', '--error', action='store_true',
                   help='Brings up the error screen for formatting')

    return p.parse_args()

def on_connect():
    logging.info('connect')
    return 'connected'


def on_push_state(*args):
    global lastpass
    # Only run screen update if the key arguments have changed since the last call. Key arguments are:
    # status
    # albumart
    # artist, album, title
    # Volume crosses mute threshold
    print(args[0])
    wasmuted = bool(lastpass['volume'] < mutethresh)
    ismuted = bool(args[0]['volume'] < mutethresh)
    wasplaying = bool(lastpass['status'] == 'play')
    isplaying = bool(args[0]['status'] == 'play')
    techstring = False
    if ((args[0]['title'] != lastpass['title'] or (wasplaying != isplaying)) and args[0]['status'] != 'stop') or \
            wasmuted != ismuted:
        lastpass = args[0]
        img = Image.new('RGBA', (display.width, display.height), color=(255, 255, 255, 0))

        # Load cover
        albumart = args[0]['albumart'].encode('ascii', 'ignore')

        # Make the album art link into a url & get it & paste it in
        if b'http://' in albumart:
            # It's already a url, which means radio, no need to do anything
            pass
        else:
            # Otherwise turn it into a url
            albumart = 'http://' + servername + ':3000' + args[0]['albumart']
        try:
            response = requests.get(albumart)
            imgart = Image.open(BytesIO(response.content))
            imgart = imgart.convert("RGBA")
            imgart = imgart.resize((coversize, coversize))
        except:
            # If there are issues getting the icon, just use a blank space
            imgart = Image.new('RGBA', (coversize, coversize), color=(255, 255, 255, 0))

        img.paste(imgart, (int((display.width - coversize) / 2), 220), imgart)

        if args[0]['status'] in ['pause', 'stop']:
            img.paste(pause_icons, (indent, 300), pause_icons)

        draw = ImageDraw.Draw(img, 'RGBA')
        fontsize = 80
        y_text = -450
        height = 80
        width = 25
        if 'artist' in args[0]:
            img, numline = writewrappedlines(img, args[0]['artist'], fontsize, y_text, height, width, fontstring)
        y_text = 160
        height = 50
        fontsize = 50
        width = 40
        if 'album' in args[0] and args[0]['album'] is not None:
            titletext = smart_truncate(args[0]['album'], length=27)
            img, numline = writewrappedlines(img, args[0]['album'], fontsize, y_text, height, width, fontstring)

        if 'stream' in args[0]:
            if str(args[0]['stream']) is 'True':
                techstring = "(" + str(args[0]['bitrate'])
            else:
                techstring = "(" + str(args[0]['stream'])
            techflag = True
        if 'samplerate' in args[0] and args[0]['samplerate'] != '':
            techstring += ", " + str(args[0]['samplerate'])
        if 'bitdepth' in args[0] and args[0]['bitdepth'] != '':
            techstring += ", " + str(args[0]['bitdepth'])
        if techflag:
            y_text = 210
            fontsize = 40
            img, numline = writewrappedlines(img, techstring + ")", fontsize, y_text, height, width, fontstring)
        y_text = 290
        fontsize = 120
        height = 120
        width = 20
        if 'title' in args[0] and args[0]['title'] is not None:
            titletext = smart_truncate(args[0]['title'], length=33)
            img, numline = writewrappedlines(img, titletext, fontsize, y_text, height, width, fontstring)

        vol_x = int(float(args[0]['volume']))

        if vol_x <= mutethresh:
            logging.info('muted')
            img.paste(mute_icons, (iconheight, 300), mute_icons)
        display_image_8bpp(display, img)
    return

def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix

# get the path of the script
script_path = os.path.dirname(os.path.abspath(__file__))
dirname = os.path.dirname(__file__)
configfile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.yaml')

# set script path as current directory
os.chdir(script_path)

# Read config and Initialise display
args = parse_args()
with open(configfile) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
logging.info("Read Config File")
logging.info(config)
if not args.virtual:
    from IT8951.display import AutoEPDDisplay

    logging.info('Initializing EPD...')

    # here, spi_hz controls the rate of data transfer to the device, so a higher
    # value means faster display refreshes. the documentation for the IT8951 device
    # says the max is 24 MHz (24000000), but my device seems to still work as high as
    # 80 MHz (80000000)
    display = AutoEPDDisplay(vcom=config['display']['vcom'], rotate=args.rotate, spi_hz=60000000)

else:
    from IT8951.display import VirtualEPDDisplay
    display = VirtualEPDDisplay(dims=(1448, 1072), rotate=args.rotate)

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
print(info['artist'])

logging.info("draw")
im = Image.open(os.path.join(picdir, 'Empty2.bmp'))
draw = ImageDraw.Draw(im)
# draw.line((0, 0) + im.size, fill=0)
# draw.line((0, im.size[1], im.size[0], 0), fill=0)
# draw.rectangle((0, 10, 20, 34), fill=0)
# draw.line((16, 60, 56, 60), fill=0)
logging.info("drawline")
draw.text((8, 10), 'Song : ' + info['title'], font=font15, fill=0)
draw.text((8, 30), 'Album : ' + info['album'], font=font15, fill=0)
draw.text((8, 50), 'by : ' + info['artist'], font=font15, fill=0)
im2 = im.transpose(method=Image.ROTATE_90)
image.paste(im2, (2, 2))
epd.displayPartial(epd.getbuffer(im2))
epd.init(epd.PART_UPDATE)

time.sleep(2)

