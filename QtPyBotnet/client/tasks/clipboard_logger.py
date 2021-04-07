from tasks.__task import Task
from utils import threaded_task


class ClipboardLogger(Task):
    """Periodically dump new clipboard contents."""
    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": False, "darwin": False}
    kwargs = {"log_time": {"type": int, "description": "Logging time in seconds", "default": 900},
              "log_frequency": {"type": int, "description": "Delay between next clipboard check", "default": 5}}

    def __init__(self, task_id):
        super(ClipboardLogger, self).__init__(task_id)
        import logging
        import threading

        self._logger = logging.getLogger(self.__class__.__name__)
        self._data = []
        self._run = threading.Event()

    @threaded_task
    def start(self, log_time=900, log_frequency=5):
        import time
        import pyperclip

        self._run.set()
        self._logger.info("Starting task {}".format(self.__class__.__name__))
        for i in range(0, log_time, log_frequency):
            if self._run.is_set():
                data = pyperclip.paste()
                if data not in self._data:
                    self._data.append(data)
                    self._logger.debug("New item in clipboard: {}".format(data))
                time.sleep(log_frequency)
            else:
                break
        return self._data

    def stop(self):
        self._run.clear()
