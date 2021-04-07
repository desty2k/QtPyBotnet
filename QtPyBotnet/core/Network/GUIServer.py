from qtpy.QtCore import Signal

from QtPyNetwork.server import QThreadedServer

from qasync import asyncSlot

from QtPyBotnet.models import Task, Module, Info


class GUIServer(QThreadedServer):
    """GUI server."""
    stop_task = Signal(int, int)
    toggle_module = Signal(int, str, bool)

    def __init__(self):
        super(GUIServer, self).__init__()

    @asyncSlot(int, dict)
    async def on_message(self, device_id: int, message: dict):
        if message.get("event_type") == "task":
            event = message.get("event")
            
            if event == "stop":
                self.stop_task.emit(message.get("bot_id"), message.get("task_id"))

        elif message.get("event_type") == "module":
            self.toggle_module.emit(message.get("bot_id"), message.get("module"), message.get("state"))

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

    @asyncSlot(Module)
    async def on_bot_module(self, module):
        self.writeAll(module.serialize())

    @asyncSlot(Info)
    async def on_bot_info(self, info):
        self.writeAll(info.serialize())
