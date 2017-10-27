'''
__author__ = "@sgript"

Sends alert to admins when a canary function is triggered
'''
import pymysql
import sys

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Alert:
    def __init__(self, database):
        self.email_config = database.get_email_config()

        self.MY_ADDRESS = self.email_config[0][1]
        self.PASSWORD = self.email_config[0][2]
        self.database_emails = database.get_admin_emails()

    def to_administrators(self, module, function, uuid, channel):
        s = smtplib.SMTP(host = self.email_config[0][3], port = self.email_config[0][4])
        s.starttls()
        s.login(self.MY_ADDRESS, self.PASSWORD)

        for email in self.database_emails:
            msg = MIMEMultipart()
            message = "The canary function {} in the {} module was ran by {} on channel at {}!".format(function, module, uuid, channel)

            msg['From'] = self.MY_ADDRESS
            msg['To'] = email[1]
            msg['Subject'] = "WARNING: Canary function used!"

            msg.attach(MIMEText(message, 'plain'))

            s.send_message(msg)
            del msg

        s.quit()
