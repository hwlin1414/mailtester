#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import socket
import asyncore
import threading

import testcase

FORMAT = "%(asctime)-15s [%(levelname)s] %(name)s: %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(format=FORMAT, level=logging.INFO, datefmt=DATEFMT)
log_formatter = logging.Formatter(fmt=FORMAT, datefmt=DATEFMT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Handler(asyncore.dispatcher_with_send):
    def __init__(self, sock, config):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.rbuf = ""
        self._config = config
    def handle_read(self):
        data = self.recv(8192)
        if data:
            self.rbuf += data
        else:
            self.close()
    def handle_close(self):
        logger.debug("mail recieved")
        token = testcase.getToken(self.rbuf)

        lock = self._config['lock']
        lock.acquire()
        for r in self._config['runtime'][:]:
            if r.check(token):
                logger.info("recieve token: {token}".format(token = r.config['token']))
                self._config['runtime'].remove(r)
        lock.release()

class Listener(asyncore.dispatcher):
    def __init__(self, config):
        asyncore.dispatcher.__init__(self)
        self._config = config
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(config['listen'])
        self.listen(socket.SOMAXCONN)
        logger.info("listen on {listen}".format(listen = config['listen']))
    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            logger.debug("accept {addr}".format(addr = addr))
            handler = Handler(sock, self._config)

class Thr(threading.Thread):
    def __init__(self, config, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        self._config = config
    def run(self):
        logger.debug("Thread Start")
        l = Listener(self._config)
        asyncore.loop()
