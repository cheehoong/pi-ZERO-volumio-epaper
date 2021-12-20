#!/usr/local/bin/python3
import cv2
import os
from PIL import Image, ImageDraw, ImageFont

# path
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')  # Points to pic directory
path = os.path.join(picdir, 'Empty2.bmp')

img = cv2.imread(path, 0)
cv2.imshow('image', img)
cv2.waitKey(0)