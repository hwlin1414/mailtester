#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import threading
import time

FORMAT = "%(asctime)-15s [%(levelname)s] %(name)s: %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(format=FORMAT, level=logging.INFO, datefmt=DATEFMT)
log_formatter = logging.Formatter(fmt=FORMAT, datefmt=DATEFMT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Thr(threading.Thread):
    def __init__(self, config, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        self._config = config
    def run(self):
        logger.debug("Thread Start")
        while True:
            logger.debug("notifier wakeup")
            lock = self._config['lock']
            lock.acquire()
            minsleep = False
            for r in self._config['runtime'][:]:
                expired = r.expired()
                if expired is True:
                    logger.warn("{token} ({host}) expired".format(token = r.config['token'], host = r.config['Host']))
                    r.notify("email timeout")
                    self._config['runtime'].remove(r)
                elif minsleep is False:
                    minsleep = expired
                elif expired < minsleep:
                    minsleep = expired
            if minsleep is False: minsleep = 10
            lock.release()
            logger.debug("sleep for {minsleep}".format(minsleep = minsleep))
            time.sleep(minsleep)
