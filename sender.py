import base64
import hashlib
import json
import logging
import socket
import struct
import time
import sys

from pprint import pformat
from threading import Thread

from drop_queue import DropQueue

log = logging.getLogger(__name__)


class Sender(Thread):
    end = False
    buffer_size = 12800
    avg_send_time = 0
    avg_count = 0

    def __init__(self, server, client_port=7777, server_port=5555):
        Thread.__init__(self)
        self.sock, self.settings = self.create_sock(server, client_port, server_port)

        self.framebuf = DropQueue(2)

    def create_sock(self, server, client_port=7777, server_port=5555):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server, client_port))

        sett = self.get_settings(sock)

        log.info(pformat(sett))

        settings = json.dumps(
            {
                "version": "std2",
                "code": self.ch_summ(sett["ref"], "_defaulttglibva"),
                "videostream": "mjpeg",
                "sensorstream": "normal",
                "sensorport": server_port,
                "sensorVersion": 1,
                "motionboost": False,
                "nolens": False,
                "convertimage": False,
                "fakeroll": False,
                "source": "None",
                "project": "Python",
                "proc": "None",
                "stroverlay": "",
            }
        ).encode("utf-8")

        sock.send(settings)

        return sock, sett

    def run(self):
        while not self.end:
            self.recv()

    def send(self):
        start_time = time.time()
        scr = self.framebuf.get()
        self.sock.send(struct.pack(">i", len(scr)))
        self.sock.send(scr)
        processed_time = time.time() - start_time
        self.avg_send_time = ((self.avg_send_time * self.avg_count) + processed_time) / (self.avg_count + 1)

        self.avg_count += 1

    def recv(self):
        try:
            t = self.sock.recv(1)
            for i in range(t.count(b"e")):
                self.send()
            if self.avg_count > 10:
                sys.stdout.write(f"\ravg send time ms: {round(self.avg_send_time * 100, 3)}")
                self.avg_count = 0
        except ConnectionResetError:
            log.info("Connection closed")
            self.end = True

    @staticmethod
    def ch_summ(ref, module):
        c = ref + module
        a = hashlib.sha1(c.encode("utf-8"))
        s = a.digest()
        c = base64.b64encode(s).decode("utf-8") + module
        return c

    def get_settings(self, sock: socket.socket):
        settings = json.loads(sock.recv(self.buffer_size).decode("utf-8"))
        settings["videoSupport"] = settings["videoSupport"].split(",")
        settings["sensorSupport"] = settings["sensorSupport"].split(",")
        return settings
