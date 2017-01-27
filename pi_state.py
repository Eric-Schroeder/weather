#! /usr/bin/env python3

import RPi.GPIO as GPIO


def pi_state():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)
    GPIO.output(17, True)

if __name__ == '__main__':
    pi_state()
