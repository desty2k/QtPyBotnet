from tasks.__task import Task


class Screenshot(Task):
    """Take screenshoot."""
    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": False, "darwin": False}

    def __init__(self, task_id):
        super(Screenshot, self).__init__(task_id)
        import logging
        import threading

        self._logger = logging.getLogger(self.__class__.__name__)
        self._run = threading.Event()

    def run(self, **kwargs):
        import mss
        import base64
        from mss.tools import to_png

        with mss.mss() as screen:
            screen_shot = screen.grab(screen.monitors[0])
            img = base64.b64encode(to_png(screen_shot.rgb, screen_shot.size)).decode()
            return {"type": "images", "images": [img]}

    def stop(self):
        self._run.clear()
