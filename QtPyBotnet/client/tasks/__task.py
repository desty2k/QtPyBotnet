import queue
import logging

from utils import threaded


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

        self.run_kwargs = {}
        self.result = result
        self.exit_code = exit_code
        self.user_activity = user_activity

        self.thread = None
        self.started = False
        self.status = queue.Queue()
        self.logger = logging.getLogger(self.__class__.__name__)

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
                "user_activity": self.user_activity,
                "result": self.result,
                "exit_code": self.exit_code,
                "state": state}

    def was_started(self):
        return self.started

    def set_run_kwargs(self, kwargs):
        self.run_kwargs = kwargs

    def get_status(self):
        return self.status.get()

    def status_available(self):
        return not self.status.empty()

    def put_status(self, value):
        self.status.put(value)

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

    @threaded
    def start(self, kwargs):
        """Check if all keyword arguments are valid and run thread."""
        for kw in self.kwargs:
            assert kw in kwargs, "Missing keyword argument {}".format(kw)
            try:
                kwargs[kw] = self.kwargs[kw].get("type")(kwargs[kw])
            except TypeError:
                raise TypeError("Invalid type for keyword argument {} expected {}."
                                .format(kw, self.kwargs[kw].get("type")))
        self.logger.debug("Starting task {}".format(self.__class__.__name__))
        self.started = True
        return self.run(**kwargs)

    def run(self, **kwargs):
        raise NotImplementedError("Run not implemented for this task!")

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
