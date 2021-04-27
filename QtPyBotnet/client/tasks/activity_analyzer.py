from tasks.__task import Task


class ActivityAnalyzer(Task):
    """Analyzes user activity."""
    platforms = ["win32", "darwin", "linux"]
    description = __doc__
    administrator = {"win32": False, "darwin": False, "linux": False}
    kwargs = {"sleep_time": {"type": int, "description": "Time to sleep between checks.", "default": 60}}

    def __init__(self, task_id):
        super(ActivityAnalyzer, self).__init__(task_id)
        import threading
        self._activity = 0
        self._run = threading.Event()

    def get_activity(self):
        return self._activity

    def run(self, **kwargs):
        sleep_time = kwargs.get("sleep_time")
        import time
        import psutil

        self._run.set()
        while self._run.is_set():
            cpu = psutil.cpu_percent() * 8
            ram = psutil.virtual_memory().percent * 2
            lvl = float(cpu+ram)/100

            if lvl >= 9.5:  # Very high
                self._activity = 5
            elif 9.5 > lvl >= 7.5:  # High
                self._activity = 4
            elif 7.5 > lvl >= 5.0:  # Medium
                self._activity = 3
            elif 5 > lvl >= 2:  # Normal
                self._activity = 2
            elif 2 > lvl > 0:  # Low
                self._activity = 1
            else:  # Not supported
                self._activity = 0
            time.sleep(sleep_time)

    def stop(self):
        self._run.clear()
