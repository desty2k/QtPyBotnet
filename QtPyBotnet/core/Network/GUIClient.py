from qtpy.QtCore import Slot, Signal

from QtPyNetwork.client import QThreadedClient


class GUIClient(QThreadedClient):
    """GUI client."""
    bot_connected = Signal(int, str, int)
    bot_disconnected = Signal(int)
    bot_updated = Signal(int, dict)

    build_message = Signal(dict)
    task_message = Signal(dict)

    start_first_setup = Signal()
    setup_options = Signal(dict)

    get_config = Signal(dict)
    config_saved = Signal()
    config_validate_error = Signal(str)

    def __init__(self):
        super(GUIClient, self).__init__(loggerName=self.__class__.__name__)
        self.message.connect(self.on_message)

    @Slot(dict)
    def on_message(self, message: dict):
        event_type = message.get("event_type")
        event = message.get("event")
        if event_type == "app":
            if event == "setup":
                self.start_first_setup.emit()

        elif event_type == "config":
            if event == "get":
                self.get_config.emit(message.get("config"))
            elif event == "saved":
                self.config_saved.emit()
            elif event == "validate_error":
                self.config_validate_error.emit(message.get("error"))

        elif event_type == "connection":
            if event == "connected":
                self.bot_connected.emit(message.get("bot_id"),
                                        message.get("ip"),
                                        message.get("port"))
            elif event == "disconnected":
                self.bot_disconnected.emit(message.get("bot_id"))

        elif event_type == "info":
            self.bot_updated.emit(message.get("bot_id"), message)

        elif event_type == "build":
            self.build_message.emit(message)

        elif event_type == "task":
            if event == "options":
                self.task_message.emit(message)
            else:
                self.bot_updated.emit(message.get("bot_id"), message)
        elif event_type == "setup":
            if event == "options":
                self.setup_options.emit(message.get("options"))

    @Slot()
    def on_get_setup_options(self):
        self.write({"event_type": "setup",
                    "event": "options"})

    @Slot()
    def on_get_config(self):
        self.write({"event_type": "config",
                    "event": "get"})

    @Slot(dict)
    def on_save_config(self, config):
        self.write({"event_type": "config",
                    "event": "save",
                    "config": config})

    @Slot()
    def on_app_close(self):
        self.write({"event_type": "app",
                    "event": "close"})

    @Slot(int, int)
    def on_stop_task(self, bot_id, task_id):
        self.write({"event_type": "task",
                    "bot_id": bot_id,
                    "task_id": task_id,
                    "event": "stop"})

    @Slot(int, int)
    def on_force_start_task(self, bot_id, task_id):
        self.write({"event_type": "task",
                    "bot_id": bot_id,
                    "task_id": task_id,
                    "event": "force_start"})

    @Slot(int, str, dict, int)
    def on_send_task(self, bot_id, task, kwargs, user_activity):
        self.write({"event_type": "task",
                    "bot_id": bot_id,
                    "task": task,
                    "kwargs": kwargs,
                    "user_activity": user_activity,
                    "event": "start"})

    @Slot()
    def on_get_tasks(self):
        self.write({"event_type": "task",
                    "event": "options"})

    @Slot()
    def on_get_build_options(self):
        self.write({"event_type": "build",
                    "event": "options"})

    @Slot(str, str, list)
    def on_start_build(self, name, icon, generators):
        self.write({"event_type": "build",
                    "event": "start",
                    "name": name,
                    "icon": icon,
                    "generators": generators})

    @Slot()
    def on_stop_build(self):
        self.write({"event_type": "build",
                    "event": "stop"})
