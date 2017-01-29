#! /usr/bin/env python3

import logging
import time

import Adafruit_BMP.BMP085 as BMP085
import Adafruit_DHT
import ntplib


class Weather:
    def __init__(self):
        self.temp = self.get_temperature()
        self.humidity = self.get_humidity()
        self.pressure = self.get_pressure()
        self.time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.get_time()))
        self.day = time.strftime('%d', time.localtime(self.get_time()))

    def get_temperature(self):
        temp1 = self.get_dht_data()[1]
        temp2 = self.get_bmp_data()[1]
        try:
            temp_c = (temp1+temp2) / 2
        except TypeError:
            if temp1 and temp2 is None:
                temp_c = 'N/A'
            elif temp1 is None:
                temp_c = temp2
            else:
                temp_c = temp1
        temp_f = round((temp_c * (9/5)) + 32)
        return temp_f

    def get_humidity(self):
        try:
            humidity = round(self.get_dht_data()[0])
        except TypeError:
            humidity = 'N/A'
        return humidity

    def get_pressure(self):
        pressure = round((self.get_bmp_data()[0] * 0.0002953), 2)
        if pressure is None:
            pressure = 'N/A'
        return pressure

    @staticmethod
    def get_dht_data():
        gpio_pin = 4
        humidity, temp_dht = Adafruit_DHT.read(Adafruit_DHT.DHT22, gpio_pin)
        return humidity, temp_dht

    @staticmethod
    def get_bmp_data():
        sensor = BMP085.BMP085()
        pressure = sensor.read_pressure()
        temp = sensor.read_temperature()
        return pressure, temp

    @staticmethod
    def get_time():
        try:
            response = ntplib.NTPClient().request('10.0.0.120')
            current_time = response.tx_time
        except (ntplib.NTPException, OSError) as err:
            print('We had an error! Please check the log file.')
            logging.error("FROM:weather/get_time:{}".format(err))
            current_time = None
        return current_time
