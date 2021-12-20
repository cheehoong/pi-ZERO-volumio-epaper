#!/usr/bin/python
# -*- coding:utf-8 -*-
import argparse
import logging
import os
import time
from configparser import ConfigParser
from PIL import Image, ImageDraw, ImageFont
from socketIO_client import SocketIO
from libz import epd2in13_V2
from libz import gt1151

logging.basicConfig(level=logging.DEBUG)
flag_t = 1

# get the path of the script
file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini')
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')  # Points to pic directory
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')

# Initialise some constants
font15 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 15)
font24 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 24)
rabbit_icon = Image.open(os.path.join(picdir, 'rabbitsq.png')).resize((30, 30)).convert(0)

# Read config setting
config = ConfigParser()
config.read(file)
print(config.sections())
volumio_host = config.get('volumio', 'volumio_host')
volumio_port = config.getint('volumio', 'volumio_port')

# Read config and Initialise display
logging.info('Initializing EPD...')
epd = epd2in13_V2.EPD_2IN13_V2()
gt = gt1151.GT1151()
GT_Dev = gt1151.GT_Development()
GT_Old = gt1151.GT_Development()

logging.info("init and Clear")
epd.init(epd.FULL_UPDATE)
gt.GT_Init()

image = Image.open(os.path.join(picdir, 'Empty2.bmp'))
epd.displayPartBaseImage(epd.getbuffer(image))
DrawImage = ImageDraw.Draw(image)
epd.init(epd.PART_UPDATE)

# Derive some constants
socketIO = SocketIO(volumio_host, volumio_port)
lastpass = {
    "artist": "none",
    "title": "none",
    "album": "none",
    "status": "none",
    "volume": 60
}


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
    artist = str(args[0]['artist'])
    title = str(args[0]['title'])
    album = str(args[0]['album'])
    status = str(args[0]['status'])
    vol_x = int(float(args[0]['volume']))
    print('Artist = ' + artist)
    print('Status = ' + status)
    lastpass = args[0]
    img = Image.open(os.path.join(picdir, 'Empty2.bmp'))
    draw = ImageDraw.Draw(img)
    if args[0]['status'] in ['pause', 'stop']:
        draw.text((8, 70), 'pause', font=font15, fill=0)
    if 'artist' in args[0]:
        draw.text((8, 50), 'by : ' + lastpass['artist'], font=font15, fill=0)
    if 'album' in args[0] and args[0]['album'] is not None:
        draw.text((8, 30), 'Album : ' + lastpass['album'], font=font15, fill=0)
    if 'title' in args[0] and args[0]['title'] is not None:
        draw.text((8, 10), 'Song : ' + lastpass['title'], font=font15, fill=0)
    if vol_x <= 1:
        logging.info('muted')
        draw.text((38, 70), 'muted', font=font15, fill=0)
    im2 = img.transpose(method=Image.ROTATE_90)
    img.paste(im2, (2, 2))
    epd.displayPartial(epd.getbuffer(im2))
    epd.init(epd.PART_UPDATE)
    return







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
