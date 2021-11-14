import socket
import struct
import math

from logging import getLogger

log = getLogger(__name__)


class OpenVR:
    radian_degrees: float

    def __init__(self):
        self.addr = ("127.0.0.1", 4242)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.connect(self.addr)
        self.radian_degrees = math.degrees(1)

    def callback(self, data):
        if "quaternion" not in data:
            return
        quaternion = data["quaternion"]
        log.debug('q: %s', quaternion)
        # WXYZ
        packet = struct.pack("4d",
                             quaternion[3] / self.radian_degrees,
                             quaternion[0] / -self.radian_degrees,
                             quaternion[1] / -self.radian_degrees,
                             quaternion[2] / self.radian_degrees)
        try:
            self.sock.sendto(packet, self.addr)
        except:
            pass
