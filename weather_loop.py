#! /usr/bin/env python3
import os


def loop():
    times = 100
    answer = input('Make sure RPi is in debug mode. [Y] to continue: ')
    if answer == 'Y':
        for x in range(times):
            print('Running {} of {}...'.format(x, times)),
            os.system("sudo ./weather_main.py")
    else:
        loop()

if __name__ == '__main__':
    loop()
