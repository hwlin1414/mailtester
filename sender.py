#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import logging.handlers
import threading

import testcase

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

def check_case(case, config):
    logger.debug("check case: {host}".format(host = case['Host']))

    lock = config['lock']
    lock.acquire()

    run = testcase.TestCase(case)
    if run.test() is True:
        logger.info("add token: {token} ({host})".format(host = case['Host'], token = run.config['token']))
        config['runtime'].append(run)

    lock.release()
    threading.Timer(case['Interval'], check_case, (case, config)).start()

class Thr(threading.Thread):
    def __init__(self, config, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        self._config = config
    def run(self):
        logger.debug("Thread Start")

        lock = self._config['lock']
        lock.acquire()
        for c in self._config['case']:
            c['online'] = True
            check_case(c, self._config)
        lock.release()
