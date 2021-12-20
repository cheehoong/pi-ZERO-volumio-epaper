import logging
import os
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from configparser import ConfigParser
from socketIO_client import SocketIO

# path
file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini')
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')  # Points to pic directory
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')
font15 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 15)
font24 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 24)
baseimage = os.path.join(picdir, 'Empty2.bmp')

# Read config setting
config = ConfigParser()
config.read(file)
print(config.sections())
volumio_host = config.get('volumio', 'volumio_host')
volumio_port = config.getint('volumio', 'volumio_port')

socketIO = SocketIO(volumio_host, volumio_port)
lastpass = {
    "artist": "none",
    "title": "none",
    "album": "none",
    "status": "none",
    "volume": 60
}


def on_push_state(*args):
    global lastpass
    cv2.destroyAllWindows()
    print(args[0])
    artist = str(args[0]['artist'])
    title = str(args[0]['title'])
    album = str(args[0]['album'])
    status = str(args[0]['status'])
    print(artist)
    print(title)
    print(album)
    print(status)
    imgC = cv2.imread(baseimage, 0)
    imgD = Image.fromarray(imgC)
    draw = ImageDraw.Draw(imgD)
    draw.text((8, 30), 'by : ' + title, font=font15, fill=0)
    draw.text((8, 50), 'by : ' + artist, font=font15, fill=0)
    vol_x = int(float(args[0]['volume']))
    if vol_x <= 1:
        logging.info('muted')
    imgC = np.array(imgD)
    cv2.imshow(volumio_host, imgC)
#    cv2.waitKey(0)
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
            pass
