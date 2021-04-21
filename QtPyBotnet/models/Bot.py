from qtpy.QtCore import QObject, Signal, Slot

from models.Events import Info, Module, Task
from QtPyNetwork.models import Device

import logging
import datetime


class Bot(Device):
    update_map = Signal(int, list)
    updated = Signal()

    def __init__(self, bot_id: int, ip: str, port: int, **kwargs):
        super(Bot, self).__init__(bot_id, ip, port)
        self.logger = logging.getLogger("BOT-{}".format(bot_id))

        # add later - uniqe number for each computer
        # ip and port may change - use mac addr?
        self.hash = None
        self.key = None

        self.public_ip = "Unknown"
        self.geolocation = "Unknown"
        self.platform = "Unknown"
        self.architecture = "Unknown"
        self.system_architecture = "Unknown"
        self.username = "Unknown"
        self.administrator = "Unknown"
        self.language = "Unknown"
        self.creation_time = datetime.datetime.now()

        self.tasks = []
        self.modules = []
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
    def serialize(self):
        return "BOT-{}; IP: {}; PORT: {}; INFO: {} TASKS: {}".format(self.id, self.ip,
                                                                     self.port, vars(self),
                                                                     [x.serialize() for x in self.tasks])

    @Slot(bytes)
    def set_custom_key(self, key: bytes):
        self.key = key

    @Slot(Info)
    def on_info_received(self, info: Info):
        data = {}
        for result in info.results:
            util = info.results.get(result)

            if result == "modules":
                for module in util:
                    ev = Module(info.get_bot_id(), module.get("name"), module.get("enabled"))
                    self.on_module_received(ev)

            elif result == "tasks":
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

    @Slot(Module)
    def on_module_received(self, module: Module):
        """Triggered when module's state changes"""
        for bot_module in self.modules:
            if bot_module.module == module.module:
                bot_module.update(module)
                return
        self.modules.append(module)
        self.updated.emit()

    @Slot(Task)
    def on_task_received(self, task: Task):
        """Triggered when bot receives new task and on finish."""
        for bot_task in self.tasks:
            if bot_task.get_id() == task.get_id():
                bot_task.update(task)
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
