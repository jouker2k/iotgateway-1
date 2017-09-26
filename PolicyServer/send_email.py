#;policy

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pymysql
import sys
sys.path.append("..")

import policy_database

class Alert:
    def __init__(self, database):
        self.email_config = database.get_email_config()

        self.MY_ADDRESS = self.email_config[0][1]
        self.PASSWORD = self.email_config[0][2]
        self.database_emails = database.get_admin_emails()

        self.emails = ["s94ahmad@gmail.com", "ahmads18@cardiff.ac.uk"]


    def to_administrators(self, function, uuid, channel):
        s = smtplib.SMTP(host = self.email_config[0][3], port = self.email_config[0][4])
        s.starttls()
        s.login(self.MY_ADDRESS, self.PASSWORD)

        for email in self.database_emails:
            msg = MIMEMultipart()
            message = "The canary function {} was ran by {} on channel at {}!".format(function, uuid, channel)

            msg['From'] = self.MY_ADDRESS
            msg['To'] = email[1]
            msg['Subject'] = "WARNING: Canary function used!"

            msg.attach(MIMEText(message, 'plain'))

            s.send_message(msg)
            del msg

        s.quit()

    def email_config(self):
        pass

if __name__ == '__main__':

    pd = policy_database.PolicyDatabase('ephesus.cs.cf.ac.uk', 'c1312433', 'berlin', 'c1312433')
    alert = Alert(pd)
    alert.to_administrators('myFunc', 'someUUID', 'someChannel')
