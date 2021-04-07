from utils import dateToStr


class Task:
    """Base class for tasks."""

    platforms = []
    description = __doc__
    administrator = {}
    experimental = False
    stop_if_disconnected = False
    kwargs = {}

    def __init__(self, task_id, result={}, exit_code=None, user_activity=0):
        super(Task, self).__init__()
        self.id = task_id

        self.result = result
        self.exit_code = exit_code
        self.user_activity = user_activity
        self.time_started = None
        self.time_finished = None

        self.thread = None

    def serialize(self):
        """Creates dict from task object."""
        if self.is_alive():
            state = "running"
        elif self.exit_code is not None:
            state = "finished"
        else:
            state = "queued"

        return {"event_type": "task",
                "task_id": self.id,
                "task": self.__class__.__name__,
                "time_started": dateToStr(self.time_started),
                "time_finished": dateToStr(self.time_finished),
                "user_activity": self.user_activity,
                "result": self.result,
                "exit_code": self.exit_code,
                "state": state}

    def set_finished(self, result, exit_code):
        """Updates task with result and exit code."""
        self.result = result
        self.exit_code = exit_code

    def set_thread(self, thread):
        """Sets thread object."""
        self.thread = thread

    def get_thread(self):
        """Returns thread."""
        return self.thread

    def start(self):
        """Start task."""
        pass

    def stop(self):
        """Exit event loop inside thread."""
        pass

    def join(self, timeout=None):
        """Wait for thread to finish."""
        if self.thread:
            return self.thread.join(timeout)

    def is_alive(self):
        """Check if thread is running."""
        if self.thread:
            return self.thread.is_alive()
