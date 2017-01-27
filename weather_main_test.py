#! /usr/bin/env python3
import logging
import os
import socket
import sys
import time

import urllib3
from peewee import *

from weather_test import Weather

HOST = '10.0.0.120'

logging.basicConfig(filename='weather.log',
                    format='%(asctime)s\n %(levelname)s:%(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.ERROR)

db = MySQLDatabase('test', host=HOST, user='eric', passwd='vopo73')


class WeatherTest(Model):
    timestamp = DateTimeField()
    temp = CharField(max_length=5)
    humidity = CharField(max_length=5)
    pressure = CharField(max_length=5)

    class Meta:
        database = db


def wifi_status():
    print('Connecting...')
    tries = 20
    for x in range(tries):
        http = urllib3.PoolManager()
        try:
            http.request('GET', HOST, retries=False)
        except urllib3.exceptions.NewConnectionError as err:
            wifi = 'off'
            sys.stdout.write("\r\x1b[K"+"Try number: "+str(x+1))
            if x == tries - 1:
                print('\nConnection error! Please check the log file.')
                logging.error(err)
        else:
            wifi = 'on'

        if wifi == 'on':
            print('Connected!')
            break


def database_connection():
    try:
        db.connect()
    except OperationalError as err:
        print('We had an error! Please check the log file.')
        logging.error(err)
        return
    db.create_tables([WeatherTest], safe=True)
    add_weather_data()


def add_weather_data():
    weather_data = Weather()
    WeatherTest.create(timestamp=weather_data.time,
                       temp=weather_data.temp,
                       humidity=weather_data.humidity,
                       pressure=weather_data.pressure)


def take_image():
    camera = picamera.PiCamera()
    camera.resolution = (1296, 972)
    time_stamp = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(Weather.get_time()))
    image_file = "/home/pi/weather/images/" + time_stamp + ".jpg"
    camera.capture(image_file)


def send_image():
    port = 12760
    s = socket.socket()
    s.settimeout(60)
    try:
        s.connect((HOST, port))
    except OSError as err:
        print('We had an error! Please check the log file.')
        logging.error(err)
        return
    image = '/home/eric/Pictures/100_2117.JPG'
    # image = max(glob.iglob('/home/pi/weather/images/*.jpg'), key=os.path.getctime)
    f = open(image, "rb")

    print('Sending...')

    l = f.read(2048)
    while l:
        s.send(l)
        l = f.read(2048)
    f.close()
    s.close()
    print('finished sending')


def shutdown():
    print('Powering Down...')
    os.system("sudo shutdown -P now")

if __name__ == '__main__':
    wifi_status()
    database_connection()
    # take_image()
    send_image()
    # shutdown()
