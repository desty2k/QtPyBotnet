from tasks.__task import Task
from utils import threaded_task


class Screenshot(Task):
    """Take screenshoot."""
    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": False, "darwin": False}
    experimental = False

    def __init__(self, task_id):
        super(Screenshot, self).__init__(task_id)
        import logging
        import threading

        self._logger = logging.getLogger(self.__class__.__name__)
        self._run = threading.Event()

    @threaded_task
    def start(self):
        import mss
        from mss.tools import to_png
        import base64

        with mss.mss() as screen:
            screen_shot = screen.grab(screen.monitors[0])
            img = base64.b64encode(to_png(screen_shot.rgb, screen_shot.size)).decode()
            return {"type": "images", "images": [img]}

    def stop(self):
        self._run.clear()
