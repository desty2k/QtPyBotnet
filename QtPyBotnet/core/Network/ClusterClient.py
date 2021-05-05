from qtpy.QtCore import Slot, Signal
from qasync import asyncSlot

from QtPyNetwork.client import QThreadedClient


class ClusterClient(QThreadedClient):
    kick_bot = Signal(int)
    move_bot = Signal(int, str, int)

    def __init__(self):
        super(ClusterClient, self).__init__(loggerName=self.__class__.__name__)
        self.message.connect(self.on_message)

    @asyncSlot(dict)
    def on_message(self, message: dict):
        event_type = message.get("event_type")
        if event_type == "connection":
            event = message.get("event")
            if event == "kick":
                self.kick_bot.emit(message.get("bot_id"))
            elif event == "move":
                self.move_bot.emit(message.get("bot_id"), message.get("ip"), message.get("port"))
        elif event_type == "start":
            event = message.get("event")
            if event == "start":
                pass
            elif event == "stop":
                pass
            elif event == "force_start":
                pass

    @asyncSlot(int, int)
    async def on_bot_connected(self, bot_id: int):
        """Kick bot from server."""
        self.write({"event_type": "connection",
                    "event": "disconnected",
                    "bot_id": bot_id})

    @asyncSlot(int, int)
    async def on_bot_disconnected(self, bot_id: int):
        """Kick bot from server."""
        self.write({"event_type": "connection",
                    "event": "disconnected",
                    "bot_id": bot_id})
