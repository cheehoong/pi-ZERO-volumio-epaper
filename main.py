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
rabbit_icon = Image.open(os.path.join(picdir, 'rabbitsq.png')).resize((100, 100)).convert('1')

# Read config setting
print(file)
config = ConfigParser()
config.read(file)
logging.info(config.sections())
volumio_host = config.get('volumio', 'volumio_host')
volumio_port = config.getint('volumio', 'volumio_port')
EPD_WIDTH = 250   # Display resolution
EPD_HEIGHT = 122  # rotated WxH screen

logging.info('Initializing EPD...')
epd = epd2in13_V2.EPD_2IN13_V2()
epd.init(epd.FULL_UPDATE)
image = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 1)
epd.displayPartBaseImage(epd.getbuffer(image))
epd.init(epd.PART_UPDATE)

logging.info("Init touch")
gt = gt1151.GT1151()
GT_Dev = gt1151.GT_Development()
GT_Old = gt1151.GT_Development()
gt.GT_Init()

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
status = 'pause'
lastpass = {
    "artist": "none",
    "title": "none",
    "album": "none",
    "status": "none",
    "volume": 60
}
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
icon_plus = u"\uE145"
icon_minus = u"\uE15B"
icon_power = u"\uE8AC"


def on_connect():
    logging.info('connect')
    return 'connected'


def bar(img_b, volume):
    position = (30, 30)
    bar_height = 20
    bar_width = 190
    draw = ImageDraw.Draw(img_b)
    filled_pixels = int(bar_width * volume / 100)
    draw.rectangle((position[0], position[1], position[1] + bar_width, position[0] + bar_height), outline=0, fill=1)
    draw.rectangle((position[0] + 4, position[1] + 4, position[1] + filled_pixels - 4, position[0] + bar_height - 4),
                   fill=0)
    draw.text((77, 100), icon_home, font=font0w, fill=0)
    draw.text((position[0] + bar_width + 10, position[1]), icon_plus, font=font0w, fill=0)
    draw.text((position[0] - 30, position[1]), icon_minus, font=font0w, fill=0)
    draw.text((position[0] + 30, position[1] - 20), icon_sound, font=font0w, fill=0)
    draw.text((position[0] + 130, position[1] - 20), str(volume) + ' %', font=font18, fill=0)
    image.paste(img_b, position)
    print('end bar')
    return


def volume_screen(volume):
    img_v = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 1)
    bar(img_v, volume)
    im2v = img_v.transpose(method=Image.ROTATE_90)
    img_v.paste(im2v, (0, 0))
    epd.displayPartial(epd.getbuffer(im2v))
    epd.init(epd.PART_UPDATE)


def main_screen(*args):
    global lastpass, status
    icon_status = icon_stop
    status = str(args[0]['status'])
    vol_x = int(float(args[0]['volume']))
    img_d = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 1)
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
    if vol_x <= 1 or args[0]['mute'] is True:
        draw.text((118, 100), icon_muted, font=font0w, fill=0)
    print(vol_x)
    print(args[0]['mute'])
    draw.text((0, 100), icon_previous, font=font0w, fill=0)
    draw.text((77, 100), icon_setting, font=font0w, fill=0)
    draw.text((155, 100), icon_status, font=font0w, fill=0)
    draw.text((230, 100), icon_next, font=font0w, fill=0)
    im2 = img_d.transpose(method=Image.ROTATE_90)
    img_d.paste(im2, (0, 0))
    epd.displayPartial(epd.getbuffer(im2))
    epd.init(epd.PART_UPDATE)


def on_push_state(*args):
    global lastpass, status
    lastpass = args[0]
    # Only run.sh screen update if the key arguments have changed since the last call. Key arguments are:
    # status # albumart # artist, album, title # Volume crosses mute threshold
    logging.info('Title = ' + lastpass['title'] + ' # Album = ' + lastpass['album'] + ' # Artist = ' + lastpass[
        'artist'] + ' # Status = ' + lastpass['status'])
    # main_screen(args[0])
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
t10 = touch_area('touch_mute', 110, 165)
tt = [t0, t1, t2, t3, t4, t5, t6, t7, t8]
r = 20
page = 'main_page'

def check_touch():
    try:
        global lastpass, status
        # Read the touch input
        gt.GT_Scan(GT_Dev, GT_Old)
        if GT_Old.X[0] == GT_Dev.X[0] and GT_Old.Y[0] == GT_Dev.Y[0]:  # and GT_Old.S[0] == GT_Dev.S[0]:
            pass
            # print("Channel 0 ...\r\n")
        else:
            if page == 'main_page':
                main_screen(lastpass)
                tt = [t1, t3, t7, t9, t10]
            for k in range(len(tt)):
                if tt[k][1] - r < GT_Dev.X[0] < tt[k][1] + r and tt[k][2] - r < GT_Dev.Y[0] < tt[k][2] + r:
                    print("Channel " + str(k) + " ...\r\n")
                    button_pressed(k)
            print("Dev X=" + str(GT_Dev.X[0]), ", Y=" + str(GT_Dev.Y[0]), ", S=" + str(GT_Dev.S[0]))
            print("Old X=" + str(GT_Old.X[0]), ", Y=" + str(GT_Old.Y[0]), ", S=" + str(GT_Old.S[0]))
            GT_Dev.X[0] = GT_Dev.Y[0] = GT_Old.X[0] = GT_Old.Y[0] = 0
    except (ValueError, RuntimeError) as e:
        print('ERROR:', e)


def main():
    # connecting to socket
    socketIO.on('pushState', on_push_state)
    # get initial state
    socketIO.emit('getState', '', on_push_state)


if __name__ == '__main__':
    main()
    try:
        while True:
            check_touch()
            socketIO.wait(seconds=0.01)
    except KeyboardInterrupt:
        socketIO.disconnect()
        flag_t = 0

        img = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 1)
        img.paste(rabbit_icon, (80, 10))
        imge = img.transpose(method=Image.ROTATE_90)
        epd.displayPartial(epd.getbuffer(imge))
        # epd.Clear(0xFF)
        # epd.init(epd.FULL_UPDATE)
        # epd.init(epd.PART_UPDATE)
        t.join()
        epd.Dev_exit()
        pass
