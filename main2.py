import logging
import time
import configparser
from socketIO_client import SocketIO

config = configparser.ConfigParser()
config.readfp(open(r'config.ini'))
volumio_host = config.get('volumio', 'volumio_host')
volumio_port = config.get('volumio', 'volumio_port')

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
    print(args[0])
    title = str(args[0]['title'])
    vol_x = int(float(args[0]['volume']))
    if vol_x <= 1:
        logging.info('muted')
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
