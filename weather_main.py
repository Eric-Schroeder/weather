#! /usr/bin/env python3
import glob
import logging
import os
import socket
import sys
import time

import RPi.GPIO as GPIO
import picamera
import urllib3
from peewee import *

from disk_log import DiskLog
from weather import Weather

HOST = '10.0.0.120'

logging.basicConfig(filename='/home/pi/weather/weather.log',
                    format='%(asctime)s\n %(levelname)s:%(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.WARNING)

db = MySQLDatabase('test', host=HOST, user='eric', passwd='vopo73')


class WeatherData(Model):
    timestamp = DateTimeField()
    temp = CharField(max_length=5)
    humidity = CharField(max_length=5)
    pressure = CharField(max_length=5)

    class Meta:
        database = db


def log_disk_usage():
    disk_log = DiskLog()
    today = Weather().day
    with open('/home/pi/weather/day.log', 'r') as file:
        day = file.read()
    if day != today:
        DiskLog.check_disk_usage(disk_log)
        with open('/home/pi/weather/day.log', 'w') as file:
            file.write(today)


def debug():
    debug = False
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    if GPIO.input(21) == 0:
        debug = True
    return debug


def log_error(err):
    print('We had an error! Please check the log file.')
    logging.error(err)


def wifi_status():
    print('Connecting...')
    tries = 20
    for x in range(tries):
        http = urllib3.PoolManager()
        try:
            http.request('GET', HOST, retries=False)
        except urllib3.exceptions.ProtocolError as err:
            wifi = 'off'
            sys.stdout.write("\r\x1b[K" + "Try number: " + str(x + 1))
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
        log_error(err)
        return
    db.create_tables([WeatherData], safe=True)
    add_weather_data()


def add_weather_data():
    weather_data = Weather()
    WeatherData.create(timestamp=weather_data.time,
                       temp=weather_data.temp,
                       humidity=weather_data.humidity,
                       pressure=weather_data.pressure)


def take_image():
    try:
        camera = picamera.PiCamera()
        camera.resolution = (1296, 972)
    except picamera.exc.PiCameraMMALError as err:
        log_error(err)
        return
    try:
        time_stamp = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(Weather.get_time()))
    except AttributeError as err:
        log_error(err)
        return
    image_file = "/home/pi/weather/images/" + time_stamp + ".jpg"
    camera.capture(image_file)


def send_image():
    port = 12760
    s = socket.socket()
    try:
        s.connect((HOST, port))
    except OSError as err:
        log_error(err)
        return
    image = max(glob.iglob('/home/pi/weather/images/*.jpg'), key=os.path.getctime)
    f = open(image, "rb")

    print('Sending...')
    try:
        l = f.read(2048)
        while l:
            s.send(l)
            l = f.read(2048)
    except socket.timeout as err:
        log_error(err)
        return
    f.close()
    s.close()
    print('finished sending')


def shutdown():
    if debug():
        print('In debug mode!...NOT powering down!')
    else:
        print('Powering Down...')
        os.system("sudo shutdown -P now")

if __name__ == '__main__':
    wifi_status()
    database_connection()
    log_disk_usage()
    take_image()
    send_image()
    shutdown()
