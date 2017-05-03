#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import logging.handlers
import sys
import time
import random
import string
import smtplib
import email
import email.parser
import email.mime
import email.mime.text

#FORMAT = '%(asctime)-15s [%(levelname)s] %(name)s %(message)s'
FORMAT = '%(name)s: [%(levelname)s] %(message)s'
DATEFMT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(format=FORMAT, level=logging.INFO, datefmt=DATEFMT)
log_formatter = logging.Formatter(fmt=FORMAT, datefmt=DATEFMT)
log_handler = logging.handlers.SysLogHandler(
    facility=logging.handlers.SysLogHandler.LOG_LOCAL3,
    address = '/dev/log'
)
log_handler.setFormatter(log_formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

DEFAULT = {
    'Title': "",
    'Host': "localhost",
    'Protocol': "smtp",
    'StartTLS': False,
    'From': "root@localhost",
    'Receiver': "root@localhost",
    'Timeout': 10,
    'Interval': 300,
    'Login': False,
    'Notification': [],
    'Message': "",
}

class TestCase():
    def __init__(self, config):
        self.config = {}
        self.config.update(DEFAULT)
        self.config.update(config)
        self.origin = config
        self.config['expire'] = int(time.time()) + self.config['Timeout']
        self.config['token'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
    def check(self, token):
        if self.config['token'] == token:
            self.origin['online'] = True
            return True
        return False
    def expired(self):
        if int(time.time()) >= self.config['expire']:
            return True
        return self.config['expire'] - int(time.time())
    def notify(self, errmsg = ""):
        if self.origin['online'] is True:
            self.origin['online'] = False
            self.config['errmsg'] = errmsg
            logger.warning("sending notify mail for error")
            smtp = smtplib.SMTP('localhost')
            for m in self.config['Notification']:
                msg = email.mime.text.MIMEText(self.config['Message'].format(**self.config))
                msg['Subject'] = 'MailTester Error: {host}'.format(host = self.config['Host'])
                msg['From'] = 'mailtester'
                msg['To'] = m
                smtp.sendmail('mailtester', [m], msg.as_string())
            smtp.quit()
    def test(self):
        try:
            if self.config['Protocol'] == "smtp":
                smtp = smtplib.SMTP(self.config['Host'], 25, timeout = 10)
            elif self.config['Protocol'] == "smtps":
                smtp = smtplib.SMTP_SSL(self.config['Host'], 465, timeout = 10)
            else:
                logger.error("unknown Protocol: {p}".format(p = self.config['Protocol']))
                raise RuntimeError("unknown Protocol")
            smtp.ehlo_or_helo_if_needed()
            if self.config['StartTLS']: smtp.starttls()
            if self.config['Login'] is not False: smtp.login(*self.config['Login'])

            msg = email.mime.text.MIMEText("MailTester Testing Mail, token: {token}".format(token = self.config['token']))
            msg['Subject'] = 'MailTester Testing: {host}'.format(host = self.config['Host'])
            msg['From'] = self.config['From']
            msg['To'] = self.config['Receiver']
            msg['X-mailtester-token'] = self.config['token']

            smtp.sendmail(self.config['From'], self.config['Receiver'], msg.as_string())
            smtp.quit()
        except:
            errmsg = "Unexpected error: {error}".format(error = sys.exc_info()[0])
            logger.error(errmsg)
            self.notify(errmsg)
            return False
        return True

def getToken(mail):
    parser = email.parser.Parser()
    content = parser.parsestr(mail)
    if content['X-mailtester-token'] is None:
        logger.info("mail doesn't have X-mailtester-token")
    return content['X-mailtester-token']
