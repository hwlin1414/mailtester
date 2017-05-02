#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import threading

import config
import listener
import notifier
import sender

FORMAT = '%(asctime)-15s [%(levelname)s] %(name)s: %(message)s'
DATEFMT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(format=FORMAT, level=logging.INFO, datefmt=DATEFMT)
log_formatter = logging.Formatter(fmt=FORMAT, datefmt=DATEFMT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info('Program Start')

config.Config["runtime"] = []
config.Config["lock"] = threading.RLock()

threads = [
    listener.Thr(config.Config),
    sender.Thr(config.Config),
    notifier.Thr(config.Config),
]

for t in threads:
    t.start()

try:
    for t in threads:
        while t.isAlive():
            t.join(1)
except KeyboardInterrupt:
    logger.info('Program Stop')
