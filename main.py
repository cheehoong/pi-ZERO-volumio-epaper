#!/usr/bin/python
# -*- coding:utf-8 -*-
import argparse
import os
import logging
import time
import yaml
from libz import epd2in13_V2
from libz import gt1151
from PIL import Image, ImageDraw, ImageFont
from socketIO_client import SocketIO
import requests

logging.basicConfig(level=logging.DEBUG)
flag_t = 1

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')  # Points to pic directory
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')
font15 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 15)
font24 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 24)

logging.info("Start initial")
epd = epd2in13_V2.EPD_2IN13_V2()
gt = gt1151.GT1151()
GT_Dev = gt1151.GT_Development()
GT_Old = gt1151.GT_Development()

logging.info("init and Clear")
epd.init(epd.FULL_UPDATE)
gt.GT_Init()


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
    if ((args[0]['title'] != lastpass['title'] or (wasplaying != isplaying)) and args[0]['status'] != 'stop') or \
            wasmuted != ismuted:
        lastpass = args[0]
        img = Image.open(os.path.join(picdir, 'Empty2.bmp'))
        draw = ImageDraw.Draw(img)
        if args[0]['status'] in ['pause', 'stop']:
            draw.text((8, 70), 'pause', font=font15, fill=0)
        if 'artist' in args[0]:
            draw.text((8, 50), 'by : ' + info['artist'], font=font15, fill=0)
        if 'album' in args[0] and args[0]['album'] is not None:
            draw.text((8, 30), 'Album : ' + info['album'], font=font15, fill=0)
        if 'title' in args[0] and args[0]['title'] is not None:
            draw.text((8, 10), 'Song : ' + info['title'], font=font15, fill=0)

        vol_x = int(float(args[0]['volume']))

        if vol_x <= mutethresh:
            logging.info('muted')
            draw.text((38, 70), 'muted', font=font15, fill=0)
        im2 = img.transpose(method=Image.ROTATE_90)
        image.paste(im2, (2, 2))
        epd.displayPartial(epd.getbuffer(im2))
    return


# get the path of the script
script_path = os.path.dirname(os.path.abspath(__file__))
dirname = os.path.dirname(__file__)
configfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yaml')

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

# Initialise some constants

rabbit_icon = Image.open('pic/rabbitsq.png').resize((300, 300)).convert("RGBA")
pause_icons = Image.open('pic/pause.png').resize((240, 240)).convert("RGBA")
mute_icons = Image.open('pic/mute.png').resize((240, 240)).convert("RGBA")

coversize = config['display']['coversize']
mutethresh = 1
indent = config['display']['indent']
servername = config['server']['name']
fontstring = config['display']['font']

# Derive some constants
iconheight = display.width-240-indent
socketIO = SocketIO(servername, 3000)
socketIO.on('connect', on_connect)
lastpass = {
  "artist": "none",
  "title": "none",
  "album": "none",
  "albumart": "none",
  "status": "none",
  "volume": 60
}


# Drawing on the image


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
im2 = im.transpose(method=Image.ROTATE_90)
image.paste(im2, (2, 2))
epd.displayPartial(epd.getbuffer(im2))
epd.init(epd.PART_UPDATE)


def main():
    while True:
        # connecting to socket
        socketIO.on('pushState', on_push_state)
        # get initial state
        socketIO.emit('getState', '', on_push_state)
        # now wait
        socketIO.wait()
        logging.info('Reconnection needed')
        time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        socketIO.disconnect()
        img = Image.open(os.path.join(picdir, 'Empty2.bmp'))
        img.paste(rabbit_icon, (80, 80), rabbit_icon)
        epd.displayPartial(epd.getbuffer(img))
        pass
