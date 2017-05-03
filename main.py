#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import logging.handlers
import threading

import config
import listener
import notifier
import sender

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

logger.info("Program Start")
config.Config['runtime'] = []
config.Config['lock'] = threading.RLock()
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
            t.join(5)
except KeyboardInterrupt:
    logger.info("Program Stop")
