#!/usr/bin/python
# -*- coding:utf-8 -*-
# https://volumio.org/forum/gpio-pins-control-volume-t2219.html
# https://pypi.python.org/pypi/socketIO-client
# https://volumio.github.io/docs/API/WebSocket_APIs.html
from collections import namedtuple
import logging
import os
import threading
from configparser import ConfigParser
from PIL import Image, ImageDraw, ImageFont
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
font0w = ImageFont.truetype(os.path.join(fontdir, 'MaterialIcons-Regular.ttf'), 20)
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
status = 'pause'
icon_song = u"\uE405"
icon_artist = u"\uE416"
icon_album = u"\uE03D"
icon_play = u"\uE039"
icon_pause = u"\uE036"
icon_stop = u"\uE047"
icon_sound = u"\uE050"
icon_muted = u"\uE04F"
icon_random = u"\uE043"
icon_home = u"\uE58C"
icon_next = u"\uE044"
icon_previous = u"\uE045"
icon_setting = u"\uE8B8"


def on_connect():
    logging.info('connect')
    return 'connected'


def bar(img_b, volume):
    bar_height = 20
    bar_width = 200
    position = (0, 0)
    draw = ImageDraw.Draw(img_b)
    filled_pixels = int(bar_width*volume/100)
    draw.rectangle((0, 0, bar_width-1, bar_height-1), outline="white", fill="#2f2f2f")
    draw.rectangle((1, 1, filled_pixels-2, bar_height-2), fill="white")
    image.paste(img_b, position)
    print('end bar')
    return


def volume_screen(volume):
    img_v = Image.open(baseimage)
    print('before bar')
    bar(img_v, volume)
    print('after bar')
    im2v = img_v.transpose(method=Image.ROTATE_90)
    img_v.paste(im2v, (0, 0))
    epd.displayPartial(epd.getbuffer(im2v))
    epd.init(epd.PART_UPDATE)


def on_push_state(*args):
    global lastpass, status
    icon_status = icon_stop
    lastpass = args[0]
    # Only run screen update if the key arguments have changed since the last call. Key arguments are:
    # status # albumart # artist, album, title # Volume crosses mute threshold
    status = str(args[0]['status'])
    vol_x = int(float(args[0]['volume']))
    logging.info('Title = ' + lastpass['title'] + ' # Album = ' + lastpass['album'] + ' # Artist = ' + lastpass[
        'artist'] + ' # Status = ' + lastpass['status'])
    img_d = Image.open(baseimage)
    draw = ImageDraw.Draw(img_d)
    if args[0]['status'] in ['pause', 'stop']:
        if status == 'pause':
            icon_status = icon_pause
        if status == 'stop':
            icon_status = icon_stop
    else:
        icon_status = icon_play
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
    draw.text((0, 100), icon_previous, font=font0w, fill=0)
    draw.text((77, 100), icon_setting, font=font0w, fill=0)
    draw.text((155, 100), icon_status, font=font0w, fill=0)
    draw.text((230, 100), icon_next, font=font0w, fill=0)
    im2 = img_d.transpose(method=Image.ROTATE_90)
    img_d.paste(im2, (0, 0))
    epd.displayPartial(epd.getbuffer(im2))
    epd.init(epd.PART_UPDATE)
    return


def button_pressed(channel):
    global status
    if channel == 0:
        print('nothing')
        # socketIO.emit('next')
    elif channel == 1:
        print('next')
        socketIO.emit('next')
    elif channel == 2:
        print('random')
        # socketIO.emit('replaceAndPlay', {"uri":"live_playlists_random_50", "title":"50 random tracks", "service":"live_playlists"})
    elif channel == 3:
        print('state', status)
        if status == 'play':
            print('pause')
            socketIO.emit('pause')
        else:
            print('play')
            socketIO.emit('play')
    elif channel == 6:
        print('volume = ' + str(lastpass['volume']))
        volume_screen(lastpass['volume'])
    elif channel == 7:
        print('previous')
        socketIO.emit('prev')


touch_area = namedtuple('touch_area', ['name', 'X', 'Y'])
t0 = touch_area('touch_nothing', 20, 20)
t1 = touch_area('touch_next', 110, 10)
t2 = touch_area('touch_random', 20, 30)
t3 = touch_area('touch_play', 110, 85)
t4 = touch_area('touch_volume_add', 20, 30)
t5 = touch_area('touch_volume_minus', 30, 20)
t6 = touch_area('touch_volume', 110, 165)
t7 = touch_area('touch_previous', 110, 230)
t8 = touch_area('touch_off', 20, 30)
t9 = touch_area('touch_home', 110, 165)
tt = [t0, t1, t2, t3, t4, t5, t6, t7, t8]
r = 20


def check_touch():
    try:
        # Read the touch input
        gt.GT_Scan(GT_Dev, GT_Old)
        if GT_Old.X[0] == GT_Dev.X[0] and GT_Old.Y[0] == GT_Dev.Y[0]:  # and GT_Old.S[0] == GT_Dev.S[0]:
            pass
            # print("Channel 0 ...\r\n")
        else:
            for k in range(len(tt)):
                if tt[k][1]-r < GT_Dev.X[0] < tt[k][1]+r and tt[k][2]-r < GT_Dev.Y[0] < tt[k][2]+r:
                    print("Channel "+str(k)+" ...\r\n")
                    button_pressed(k)
            print("Dev X=" + str(GT_Dev.X[0]), ", Y=" + str(GT_Dev.Y[0]), ", S=" + str(GT_Dev.S[0]))
            print("Old X=" + str(GT_Old.X[0]), ", Y=" + str(GT_Old.Y[0]), ", S=" + str(GT_Old.S[0]))
            GT_Dev.X[0] = GT_Dev.Y[0] = GT_Old.X[0] = GT_Old.Y[0] = 0
    except (ValueError, RuntimeError) as e:
        print('ERROR:', e)


def main():
    #    while True:
    # connecting to socket
    socketIO.on('pushState', on_push_state)
    # get initial state
    socketIO.emit('getState', '', on_push_state)
    logging.info('Reconnection needed')


if __name__ == '__main__':
    main()
    try:
        while True:
            check_touch()
            socketIO.wait(seconds=0.01)
    except KeyboardInterrupt:
        socketIO.disconnect()
        flag_t = 0
#        epd.Clear(0xFF)
        img = Image.open(os.path.join(picdir, 'Empty2.bmp'))
        img.paste(rabbit_icon, (80, 10))
        imge = img.transpose(method=Image.ROTATE_90)
        epd.displayPartial(epd.getbuffer(imge))
        epd.sleep()
        t.join()
        epd.Dev_exit()
        pass
