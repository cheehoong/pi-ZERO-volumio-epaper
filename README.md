# pi-ZERO-volumio-epaper
###

<p align="center">
<img src="https://www.waveshare.com/img/devkit/LCD/2.13inch-Touch-e-Paper-HAT-with-case/2.13inch-Touch-e-Paper-HAT-with-case-details-1.jpg"
</p>

## Basic information:
This project build using Raspberry Pi ZERO 2 W using the 2.13inch e-paper HAT module.
- [2.13inch Touch e-Paper HAT](https://www.waveshare.net/wiki/2.13inch_Touch_e-Paper_HAT)
- [Raspberry Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w)
- [ABS Case](https://www.waveshare.com/2.13inch-Touch-e-Paper-HAT-with-case.htm)

## Install and config Volumio 3
- [volumio](https://volumio.com/en/get-started)
- 

## Installation library

python3
```bash
    sudo apt-get update
    sudo apt-get install python3-pip
    sudo apt-get install python3-pil
    sudo apt-get install python3-numpy
    sudo pip3 install RPi.GPIO
    sudo pip3 install spidev
```

## Basic use:
Since this project is a comprehensive project, you may need to read the following for use:
You can view the test program in the examples\ directory.
Please note which ink screen you purchased.
Chestnut 1:
    If you purchased 2.9inch Touch e-Paper HAT, then you should execute the command:
        sudo python TP2in9_test.py
    or
        sudo python3 TP2in9_test.py

## Overclocking
The Zero 2 can easily be overclocked from 1.0 GHz to 1.3 GHz.
To do this, insert the following in /boot/config.txt and restart

1
over_voltage = 6
2
arm_freq = 1300
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
