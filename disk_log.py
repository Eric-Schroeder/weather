#! /usr/bin/env python3
import logging
import re
import smtplib
import subprocess


class DiskLog:
    logging.basicConfig(filename='/home/pi/weather/disk_space.log',
                        format='%(asctime)s\n %(levelname)s:%(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)

    def check_disk_usage(self):
        disk_limit = 90
        sender = 'my.rpi.weather.station@gmail.com'
        reciver = ['eric.mi.schroeder@gmail.com']
        subject = 'Weather Station Disk Full!'
        text = "The HDD on your weather station is at or above " \
               + str(disk_limit) \
               + "%. Please do something about this."
        gmail_user = 'my.rpi.weather.station@gmail.com'
        gmail_pwd = '??whyASK!'
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (sender, ", ".join(reciver), subject, text)

        if self.get_disk_used() >= disk_limit:
            try:
                logging.info('Disk usage at {}%'.format(self.get_disk_used()))
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.ehlo()
                server.starttls()
                server.login(gmail_user, gmail_pwd)
                server.sendmail(sender, reciver, message)
                server.close()
            except smtplib.SMTPAuthenticationError:
                logging.error("Could not send 'disk full' email.")
        else:
            logging.info('Disk usage at {}%'.format(self.get_disk_used()))
            print(self.get_disk_used())

    @staticmethod
    def get_disk_used():
        disk = str(subprocess.check_output("df /home", shell=True))
        disk_used = re.findall('\d{1,3}?(?=%)', disk)
        disk_used = ''.join(disk_used)
        disk_used = int(disk_used)
        return disk_used
