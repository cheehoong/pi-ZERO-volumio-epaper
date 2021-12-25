#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
import os
import time
import threading
from configparser import ConfigParser
from PIL import Image, ImageDraw, ImageFont
from six import unichr
from socketIO_client import SocketIO
from libz import epd2in13_V2
from libz import gt1151

logging.basicConfig(level=logging.INFO)

# get the path of the script
file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini')
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')  # Points to pic directory
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')

# Initialise some constants
font18 = ImageFont.truetype(os.path.join(fontdir, 'Dengl.ttf'), 18)
font20 = ImageFont.truetype(os.path.join(fontdir, 'Dengl.ttf'), 20)
font0w = ImageFont.truetype(os.path.join(fontdir, 'webdings.ttf'), 20, encoding="symb")
rabbit_icon = Image.open(os.path.join(picdir, 'rabbitsq.png')).resize((100, 100)).convert(0)
baseimage = os.path.join(picdir, 'Empty2.bmp')

# Read config setting
config = ConfigParser()
config.read(file)
logging.info(config.sections())
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

image = Image.open(baseimage)
epd.displayPartBaseImage(epd.getbuffer(image))
DrawImage = ImageDraw.Draw(image)
epd.init(epd.PART_UPDATE)

flag_t = 1


def pthread_irq():
    print("pthread running")
    while flag_t == 1:
        if gt.digital_read(gt.INT) == 0:
            GT_Dev.Touch = 1
        else:
            GT_Dev.Touch = 0
    print("thread:exit")


t = threading.Thread(target=pthread_irq)
# t.setDaemon(True)
t.daemon = True
t.start()

# Derive some constants
socketIO = SocketIO(volumio_host, volumio_port)
lastpass = {
    "artist": "none",
    "title": "none",
    "album": "none",
    "status": "none",
    "volume": 60
}

icon_song = unichr(0xF000 + 0xAF)
icon_artist = unichr(0xF000 + 0xB1)
icon_album = unichr(0xF000 + 0xB3)
icon_play = unichr(0xF000 + 0x34)
icon_pause = unichr(0xF000 + 0x3B)
icon_stop = unichr(0xF000 + 0x3C)
icon_sound = unichr(0xF000 + 0x58)


def on_connect():
    logging.info('connect')
    return 'connected'


def on_push_state(*args):
    global lastpass
    icon_status = icon_stop
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
    logging.info('Artist = ' + artist)
    logging.info('Status = ' + status)
    lastpass = args[0]
    img_d = Image.open(baseimage)
    #    img_c = cv2.imread(baseimage, 0)
    #    img_d = Image.fromarray(img_c)
    draw = ImageDraw.Draw(img_d)
    if args[0]['status'] in ['pause', 'stop']:
        if status == 'pause':
            icon_status = icon_pause
        if status == 'stop':
            icon_status = icon_stop
    else:
        icon_status = icon_play
    draw.text((120, 100), icon_status, font=font0w, fill=0)
    if 'artist' in args[0]:
        draw.text((8, 50), icon_artist, font=font0w, fill=0)
        draw.text((28, 50), lastpass['artist'], font=font18, fill=0)
    if 'album' in args[0] and args[0]['album'] is not None:
        draw.text((8, 30), icon_album, font=font0w, fill=0)
        draw.text((28, 30), lastpass['album'], font=font18, fill=0)
    if 'title' in args[0] and args[0]['title'] is not None:
        draw.text((8, 10), icon_song, font=font0w, fill=0)
        draw.text((28, 10), lastpass['title'], font=font18, fill=0)
    if vol_x <= 1:
        logging.info('muted')
        draw.text((38, 70), 'muted', font=font18, fill=0)
    im2 = img_d.transpose(method=Image.ROTATE_90)
    img_d.paste(im2, (2, 2))
    epd.displayPartial(epd.getbuffer(im2))
    epd.init(epd.PART_UPDATE)
    return


def touch():
    # Read the touch input
    gt.GT_Scan(GT_Dev, GT_Old)
    if GT_Old.X[0] == GT_Dev.X[0] and GT_Old.Y[0] == GT_Dev.Y[0] and GT_Old.S[0] == GT_Dev.S[0]:
        print("Po ...\r\n")

    if 100 < GT_Dev.X[0] < 140 and 80 < GT_Dev.Y[0] < 120:
        print("Photo ...\r\n")
    print(GT_Dev.X[0])
    print(GT_Dev.Y[0])
    print(GT_Dev.S[0])
    print(GT_Old.X[0])
    print(GT_Old.Y[0])
    print(GT_Old.S[0])

def main():
    while True:
        # connecting to socket
        socketIO.on('pushState', on_push_state)
        # get initial state
        socketIO.emit('getState', '', on_push_state)
        # now wait
        touch()
#        socketIO.wait()
        logging.info('Reconnection needed')
        time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        socketIO.disconnect()
        img = Image.open(os.path.join(picdir, 'Empty2.bmp'))
        img.paste(rabbit_icon, (80, 10))
        imge = img.transpose(method=Image.ROTATE_90)
        epd.displayPartial(epd.getbuffer(imge))
        pass