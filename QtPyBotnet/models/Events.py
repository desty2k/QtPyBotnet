from datetime import datetime

from qtpy.QtCore import Signal, QObject

"""
Event types:
    Event:
        Base class.
        - id - event id
        - bot_id - bot id
        - time_created - time of event creation
    
    Task: 
        Executes tasks from tasks module.
        - task - command
        - result - command results
        - exit_code - command exit_code 1 - fail, 0 - success
        - completed - task completed or not
    
    Info: 
        Simmilar to task. Executes utilities only. Can run multiple at once.
        - info - list of requested info (names of utilities)
        - results - list of results of executing info
        - exit_codes - list of exit codes
        - completed - if request completed
    
    Module:
        Holds module state.
        - module - module name
        - enabled - module state True/False
"""  # noqa


class Event(QObject):
    """Bot event"""
    updated = Signal()

    def __init__(self, bot_id: int):
        super(Event, self).__init__()
        self.bot_id = bot_id
        self.time_created = datetime.now()

    def get_bot_id(self):
        return self.bot_id


class Module(Event):
    """Bot module"""

    def __init__(self, bot_id: int, module: str, enabled: bool):
        super(Module, self).__init__(bot_id)
        self.module = module
        self.enabled = enabled

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    def is_enabled(self):
        return self.enabled

    def update(self, module):
        self.set_enabled(module.is_enabled())

    def to_string(self):
        return "BOT-{}; MODULE: {}, ENABLED: {}".format(self.bot_id, self.module, self.enabled)

    def serialize(self):
        return {"event_type": "module",
                "bot_id": self.bot_id,
                "module": self.module,
                "enabled": self.enabled}

    def deserialize(self, kwargs: dict):
        # if any fails values attributes wont be changed
        bot_id = int(kwargs.get("bot_id"))
        module = str(kwargs.get("module"))
        enabled = bool(kwargs.get("enabled"))

        self.bot_id = bot_id
        self.module = module
        self.enabled = enabled


class Info(Event):
    """Bot info request - util request"""

    def __init__(self, bot_id: int, info: list, state: str, results: dict = {}):
        super(Info, self).__init__(bot_id)
        self.info = info
        self.results = results

        self.running = False
        self.finished = False

        self.state = state
        if state == "running":
            self.set_running()
        elif state == "finished":
            self.set_finished(self.results)

    def is_running(self):
        return self.running

    def is_finished(self):
        return self.finished

    def set_running(self):
        self.finished = False
        self.running = True
        self.state = "running"

    def set_finished(self, results: dict):
        self.results = results
        self.running = False
        self.finished = True
        self.state = "finished"

    def get_results(self):
        return self.results

    def serialize(self):
        return {"event_type": "info",
                "bot_id": self.bot_id,
                "info": self.info,
                "results": self.results,
                "state": self.state}

    def deserialize(self, kwargs: dict):
        # if any fails values attributes wont be changed
        bot_id = int(kwargs.get("bot_id"))
        info = dict(kwargs.get("info"))
        results = dict(kwargs.get("results"))
        state = str(kwargs.get("state"))

        self.bot_id = bot_id
        self.info = info
        self.results = results
        self.state = state

        if self.state == "running":
            self.set_running()
        elif self.state == "finished":
            self.set_finished(self.results)

    def update(self, info):
        if info.is_running():
            self.set_running()
        elif info.is_finished():
            self.set_finished(info.get_results())
        self.updated.emit()


class Task(Event):
    """Bot task"""

    def __init__(self, bot_id: int, task_id: int, task: str, state: str, result: dict = {}, exit_code: int = None):
        super(Task, self).__init__(bot_id)
        self.id = task_id

        self.task = task
        self.result = result
        self.exit_code = exit_code
        self.user_activity = 0

        self.running = False
        self.finished = False
        self.state = state

        self.time_started = None
        self.time_finished = None

        if state == "running":
            self.set_running()
        elif state == "finished":
            self.set_finished(self.result, self.exit_code)

    def get_id(self):
        return self.id

    def is_running(self):
        return self.running

    def is_finished(self):
        return self.finished

    def set_running(self):
        self.finished = False
        self.running = True
        self.state = "running"

    def set_finished(self, result: dict = {}, exit_code: int = None):
        self.result = result
        self.exit_code = exit_code
        self.running = False
        self.finished = True
        self.state = "finished"

    def get_result(self):
        return self.result

    def get_exit_code(self):
        return self.exit_code

    def update(self, task):
        if task.is_running():
            self.set_running()
        elif task.is_finished():
            self.set_finished(task.get_result(), task.get_exit_code())

    def serialize(self):
        return {"event_type": "task",
                "bot_id": self.bot_id,
                "task_id": self.id,
                "task": self.task,
                "result": self.result,
                "exit_code": self.exit_code,
                "state": self.state}

    def deserialize(self, kwargs: dict):
        # if any fails values attributes wont be changed
        bot_id = int(kwargs.get("bot_id"))
        task_id = int(kwargs.get("task_id"))
        task = dict(kwargs.get("task"))
        result = dict(kwargs.get("result"))
        exit_code = int(kwargs.get("exit_code"))
        state = str(kwargs.get("state"))

        self.bot_id = bot_id
        self.id = task_id
        self.task = task
        self.result = result
        self.exit_code = exit_code
        self.state = state

        if self.state == "running":
            self.set_running()
        elif self.state == "finished":
            self.set_finished(self.result, self.exit_code)

    def to_string(self):
        return "TASK-{}; BOT-{}; TASK: {}, RESULT: {}, EXIT-CODE: {}".format(self.id, self.bot_id,
                                                                             self.task, self.result,
                                                                             self.exit_code)
