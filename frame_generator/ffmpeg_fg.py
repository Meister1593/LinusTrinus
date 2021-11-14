import os
import subprocess
import time
import re

from typing import Optional
from logging import getLogger
from threading import Thread

from drop_queue import DropQueue

log = getLogger(__name__)


class WindowData:
    window_id: Optional[int]
    width = 0
    height = 0
    bound_x = 0
    bound_y = 0

    def __init__(self, window_id: Optional[int], width: int = 0, height: int = 0, bound_x: int = 0, bound_y: int = 0):
        self.window_id = window_id
        self.width = width
        self.height = height
        self.bound_x = bound_x
        self.bound_y = bound_y


class FfmpegFrameGenerator(Thread):
    end = False
    framebuf: DropQueue

    window_moved = False

    width = 640
    height = 480

    bound_x = "+0"
    old_bound_x = "+0"
    bound_y = "+0"
    old_bound_y = "+0"

    framerate = 60
    optirun = False
    vsync = 2

    buffer_size = 1024 * 2

    def __init__(self, settings: dict, buf: DropQueue):
        super().__init__()
        self.framebuf = buf
        self.settings = settings

    @property
    def video_size(self) -> str:
        return f"{self.width}x{self.height}"

    @property
    def boundaries(self) -> str:
        return f"{self.bound_x},{self.bound_y}"

    @staticmethod
    def api(optirun=False, **kwargs) -> str:
        cmd = "ffmpeg -f x11grab"
        if optirun:
            cmd = "optirun " + cmd
        for i in kwargs.items():
            cmd += " -%s %s" % i
        cmd += " -"
        return cmd

    def get_window_data_from_user(self, window_name: str, is_parallel: bool) -> WindowData:
        while True:
            p = subprocess.Popen(
                f'xwininfo -name "{window_name}"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            text = p.communicate()[0]
            window_id = re.findall(r"Window id: 0x([\da-f]+)", text.decode())
            if window_id:
                window_id = int(window_id[0], 16)
                window_data = re.findall(r"-geometry (\d+)x(\d+)([-+]\d*)([-+]\d*)", text.decode())[0]
                width = window_data[0]
                height = window_data[1]
                bound_x = window_data[2]
                bound_y = window_data[3]
                if not is_parallel:
                    return WindowData(window_id, width, height, bound_x, bound_y)

                self.window_moved = (bound_x != self.old_bound_x) or (bound_y != self.old_bound_y)
                self.old_bound_x = bound_x
                self.old_bound_y = bound_y
                time.sleep(0.5)
            else:
                return WindowData(None)

    def run(self):
        self.end = False

        window_data = WindowData(None)
        while not window_data.window_id:
            window_data = self.get_window_data_from_user("SteamVR Compositor", False)

        self.width = window_data.width
        self.height = window_data.height
        self.bound_x = window_data.bound_x
        self.bound_y = window_data.bound_y

        watcher_task = self.get_window_data_from_user
        watcher_thread = Thread(target=watcher_task, args=("SteamVR Compositor", True))
        watcher_thread.start()
        while not self.end:
            window_data = self.get_window_data_from_user("SteamVR Compositor", False)
            self.width = window_data.width
            self.height = window_data.height
            self.bound_x = window_data.bound_x
            self.bound_y = window_data.bound_y

            params = {
                "loglevel": "error",
                "framerate": self.framerate,
                "video_size": self.video_size,
                "i": f"%s{self.boundaries}" % os.getenv("DISPLAY", ":0.0"),
                'qmin:v': 1,
                'qmax:v': 8,
                "f": "mjpeg",
                "vsync": self.vsync,
            }

            ffmpeg_cmd = self.api(self.optirun, **params)
            log.info("ffmpeg cmd: %s", ffmpeg_cmd)
            p = subprocess.Popen(
                ffmpeg_cmd.split(),
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )

            data = bytearray()
            start = -1
            while not self.end and not self.window_moved:
                data += p.stdout.read(self.buffer_size)

                if start == -1:
                    start = data.find(b"\xFF\xD8\xFF")
                    continue
                else:
                    end = data.find(b"\xFF\xD9")

                if end != -1 and start != -1:
                    frame = data[start: end + 1]
                    self.framebuf.put(frame)

                    data = data[end + 2:]
                    start = -1
            p.kill()
            if self.window_moved:
                self.window_moved = False
            log.info("FrameGenerator end")
