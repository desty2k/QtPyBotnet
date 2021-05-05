from datetime import datetime

from qtpy.QtCore import Signal, QObject


class Event(QObject):
    """Bot event"""
    updated = Signal()

    def __init__(self, bot_id: int):
        super(Event, self).__init__()
        self.bot_id = bot_id
        self.time_created = datetime.now()

    def get_bot_id(self):
        return self.bot_id


class Info(Event):
    """Bot info request - util request"""

    def __init__(self, bot_id: int, info: list, results: dict = {}):
        super(Info, self).__init__(bot_id)
        self.info = info
        self.results = results

    def get_results(self):
        return self.results

    def create(self):
        return {"event_type": "info",
                "info": self.info}

    def serialize(self):
        return {"event_type": "info",
                "bot_id": self.bot_id,
                "info": self.info,
                "results": self.results}

    def deserialize(self, kwargs: dict):
        # if any fails values attributes wont be changed
        bot_id = int(kwargs.get("bot_id"))
        info = dict(kwargs.get("info"))
        results = dict(kwargs.get("results"))

        self.bot_id = bot_id
        self.info = info
        self.results = results


class Task(Event):
    """Bot task"""

    def __init__(self, bot_id: int, task_id: int, task: str, kwargs: dict = {},
                 result: dict = None, exit_code: int = None):
        super(Task, self).__init__(bot_id)
        self.id = task_id

        self.task = task
        self.kwargs = kwargs
        self.result = result
        self.exit_code = exit_code
        self.user_activity = 0

        self.time_created = None
        self.time_started = None
        self.time_finished = None
        self.state = None

    def get_id(self):
        return self.id

    def is_running(self):
        return self.time_started is not None

    def is_finished(self):
        return self.time_finished is not None

    def update(self, task):
        if task.is_running():
            self.set_running(task.time_started)
        if task.is_finished():
            self.set_finished(task.time_finished, task.result, task.exit_code)

    def set_created(self, time_started):
        self.time_created = time_started
        self.state = "Queued"

    def set_running(self, time_started):
        self.time_started = time_started
        self.state = "Running"

    def set_finished(self, time_finished, result, exit_code):
        self.time_finished = time_finished
        self.result = result
        self.exit_code = exit_code
        self.state = "Finished"

    def create(self):
        return {"event_type": "task",
                "task": self.task,
                "kwargs": self.kwargs,
                "task_id": self.id,
                "user_activity": self.user_activity}

    def serialize(self):
        return {"event_type": "task",
                "task": self.task,
                "kwargs": self.kwargs,
                "bot_id": self.bot_id,
                "task_id": self.id,
                "result": self.result,
                "exit_code": self.exit_code,
                "time_created": self.time_created,
                "time_started": self.time_started,
                "time_finished": self.time_finished,
                "user_activity": self.user_activity}

    def deserialize(self, kw: dict):
        bot_id = int(kw.get("bot_id"))
        task_id = int(kw.get("task_id"))
        task = str(kw.get("task"))
        kwargs = dict(kw.get("kwargs"))
        result = kw.get("result")
        exit_code = kw.get("exit_code")
        time_created = kw.get("time_created")
        time_started = kw.get("time_started")
        time_finished = kw.get("time_finished")

        self.bot_id = bot_id
        self.id = task_id
        self.task = task
        self.kwargs = kwargs
        self.result = result
        self.exit_code = exit_code
        self.time_created = time_created
        self.time_started = time_started
        self.time_finished = time_finished
        self.update(self)
