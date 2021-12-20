from socketIO_client import SocketIO, WebsocketTransport
import sys
import os
import six
import socket
import websocket

def recv_packet_unicode(self):
    try:
        packet_text = self._connection.recv()
    except websocket.WebSocketTimeoutException as e:
        raise TimeoutError('recv timed out (%s)' % e)
    except websocket.SSLError as e:
        raise ConnectionError('recv disconnected by SSL (%s)' % e)
    except websocket.WebSocketConnectionClosedException as e:
        raise ConnectionError('recv disconnected (%s)' % e)
    except socket.error as e:
        raise ConnectionError('recv disconnected (%s)' % e)
    try:
        encoded = six.b(packet_text)
    except (UnicodeEncodeError):
        # print("six.b latin-l encoding fails, switching to six.u unicode uncoding")
        pass
    else:
        encoded = six.u(packet_text)
    engineIO_packet_type, engineIO_packet_data = parse_packet_text(encoded)
    yield engineIO_packet_type, engineIO_packet_data

# Set the new recv_packet_unicode method
WebsocketTransport.recv_packet = recv_packet_unicode