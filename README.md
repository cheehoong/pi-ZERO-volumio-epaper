# pi-ZERO-volumio-epaper
###

<p align="center">
<img src="https://www.waveshare.com/img/devkit/LCD/2.13inch-Touch-e-Paper-HAT-with-case/2.13inch-Touch-e-Paper-HAT-with-case-details-1.jpg"
</p>

# STILL IN WORKS .... far away from running ...
    
## Basic information:
This project build using Raspberry Pi ZERO 2 W using the 2.13inch e-paper HAT module.
### Hardware
- [2.13inch Touch e-Paper HAT](https://www.waveshare.net/wiki/2.13inch_Touch_e-Paper_HAT)
- [Raspberry Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w)
- [ABS Case](https://www.waveshare.com/2.13inch-Touch-e-Paper-HAT-with-case.htm)
- [Get yourself a nice USB speaker](https://www.aliexpress.com/i/1005001710457608.html)

## Install Volumio 3
- [volumio](https://volumio.com/en/get-started) <-- Download and install volumio 3


<details><summary>If you not able to boot volumio 3 on Raspberry pi ZERO 2 W, Try this..</summary>
<p>

</p>
<p>
- Change new SD-card (could be faulty SD-card)
</p>
<p>
- Setup your SD-card on raspberry pi 3/4, (basic setup + wifi) then move the SD-card to your Raspberry pi ZERO
</p>
</details>

## Config volumio 3
### To turn on SPI i/o
```bash
sudo nano /boot/config.ini
```
Then add to last line
```bash
dtparam=spi=on
```
or
```bash
dtparam=i2c=on,spi=on
```

## Installation library

### Step 1
Install python3 and packages
```bash
    sudo apt-get update
    sudo apt-get install python3-pip
    sudo apt-get install python3-pil
    sudo apt-get install python3-numpy 
    sudo apt-get install python3-socketio-client
    sudo pip3 install RPi.GPIO
    sudo pip3 install spidev
    sudo pip3 install -U PyYAML

```
### Step 2
Install pi-ZERO-volumio-epapper

```bash
git clone https://github.com/cheehoong/pi-ZERO-volumio-epaper.git
chmod +x ~/pi-ZERO-volumio-epapper/pi-volumio-epaper.py
sudo cp ~/pi-ZERO-volumio-epapper/pi-volumio-epaper.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pi-volumio-epaper.service
reboot
````
## Installation steps (Update)
```bash
sudo systemctl disable pi-volumio-epaper.service
sudo rm -r pi-ZERO-volumio-epaper
```
Then redo Step 2:

## Run

```bash
sudo git clone https://github.com/cheehoong/pi-ZERO-volumio-epaper
sudo python3 pi-volumio-epapper.py
sudo python3 main.py
```

## Chinese Character display

问题
当接收到中文消息时出现下方错误，简单说就是编码问题。
```bash
Traceback (most recent call last):
  File "sub.py", line 24, in <module>
    socketIO.wait()
  File "/usr/local/lib/python3.5/site-packages/socketIO_client/__init__.py", line 232, in wait
    self._process_packets()
  File "/usr/local/lib/python3.5/site-packages/socketIO_client/__init__.py", line 254, in _process_packets
    for engineIO_packet in self._transport.recv_packet():
  File "/usr/local/lib/python3.5/site-packages/socketIO_client/transports.py", line 155, in recv_packet
    six.b(packet_text))
  File "/usr/local/lib/python3.5/site-packages/six.py", line 620, in b
    return s.encode("latin-1")
UnicodeEncodeError: 'latin-1' codec can't encode characters in position 21-27: ordinal not in range(256)
```
解决方法
找到socketIO_client的安装路径，例中跟six.py在同一目录下，路径是/usr/local/lib/python3.5/site-packages/socketIO_client/.
或者是(/usr/local/lib/python3/dist-packages/socketIO_client/)
找到socketIO_client文件夹下的transports.py文件

用编辑器打开transports.py，在144行左右的位置找到recv_packet函数
```bash

def recv_packet(self):
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
    engineIO_packet_type, engineIO_packet_data = parse_packet_text(
        six.b(packet_text))
    yield engineIO_packet_type, engineIO_packet_data
```
修改倒数第二行six.b(packet_text))为six.u(packet_text))，修改后保存.

再次运行代码接收中文消息，代码正常运行.

## Pycharm
```bash
pip install -U socketIO-client
```

## Overclocking (Optional)
The Zero 2 can easily be overclocked from 1.0 GHz to 1.3 GHz.
To do this, insert the following in /boot/config.txt and restart

```bash
over_voltage = 6
arm_freq = 1300
```
The CPU then throttles earlier under load or gets hot faster.
Even without over_voltage, my Zero 2 runs stably at 1.2 GHz in a standard housing. Idle temps ~ 42 ° C

<p align="center">
<img src="https://assets.raspberrypi.com/static/51035ec4c2f8f630b3d26c32e90c93f1/2b8d7/zero2-hero.webp" alt width="603" height=""400"
</p>

## Power consumption
Unfortunately, the higher performance also leads to higher power consumption, which is only relevant for battery operation.

| Zero 1 W            | 0.9 W       |
|---------------------|-------------|
| Zero 2 W (1 core)   | 1.0 W       |
| Zero 2 W (4 cores)  | 2.2 W       |

CPU stress test
The idle power consumption of the Zero 2 is only slightly higher than that of the Zero 1 (0.5 W instead of 0.4 W).
If, for example, you want to tease out a little more battery life in timelapse projects where performance is not important, you can deactivate 3 of the 4 CPU cores:
To do this , you edit them /boot/cmdline.txt and insert them maxcpus=1after console=tty1. After a restart, only one of the 4 CPU cores is available. This means that in the event of a CPU spike, less power is used. Depending on how long the timelapse intervals are, that could be relevant.

In general, the Zero 2 W, like the Zero 1 W, can be operated on a USB (2.0 or 3.0) port, e.g. on a laptop, since it does not consume more than 500 mA at 5V = 2.5 W.
