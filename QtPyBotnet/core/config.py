import os
import json
import psutil
import socket
import logging
import ipaddress

from qtpy.QtCore import Signal, QObject, Slot

from core.crypto import generate_key
from core.importer import get_subclassess_by_name, function_importer


class ConfigManager(QObject):
    """Manages and loads config files."""
    config_missing = Signal()
    config_read = Signal(dict)

    config_get = Signal(int, dict)
    config_saved = Signal(int)
    config_error = Signal(int, str)
    validation_error = Signal(int, str)

    available_tasks = Signal(int, list)
    available_infos = Signal(int, list)
    
    setup_options = Signal(int, dict)

    def __init__(self):
        super(ConfigManager, self).__init__(None)
        self.__config = {}
        self.__key = ""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__config_path = ".\\QtPyBotnet.cfg"
        self.__indent = 2

    def setValue(self, key, value):
        if self.__config_path:
            self.__config[key] = value
        else:
            raise Exception("Config not loaded")

    def value(self, key):
        if self.__config_path:
            return self.__config[key]
        else:
            raise Exception("Config not loaded")

    @Slot(int, dict)
    def save(self, device_id, config: dict):
        try:
            self.logger.info("Recevied config save request from {}: {}".format(device_id, config))
            ipaddress.ip_address(config.get("gui_ip"))
            ipaddress.ip_address(config.get("c2_ip"))
        except Exception as e:
            self.logger.warning("Config validation failed")
            self.validation_error.emit(device_id, str(e))
            return

        try:
            with open(self.__config_path, "w+") as f:
                data = json.dumps(config, indent=self.__indent)
                f.write(data)
            self.config_saved.emit(device_id)
            self.logger.info("Config written in {}".format(self.__config_path))
        except Exception as e:
            self.config_error.emit(device_id, "Failed to create config: {}".format(e))

    @Slot(int)
    def get(self, device_id):
        self.config_get.emit(device_id, self.__config)

    @Slot(int)
    def load(self) -> dict:
        if self.config_exists():
            data = open(self.__config_path, "r").read().encode()
            try:
                self.__config = json.loads(data)
                return self.__config
            except json.JSONDecodeError:
                self.config_error.emit("Config is not valid JSON.")
            except Exception as e:
                self.config_error.emit("Failed to decrypt config file: {}".format(e))
        else:
            self.config_missing.emit()

    def config_exists(self):
        return os.path.isfile(self.__config_path)

    def delete_config(self):
        if self.config_exists():
            os.remove(self.__config_path)

    @staticmethod
    def get_tasks():
        return get_subclassess_by_name("./client/tasks", "tasks.__task.Task")

    @staticmethod
    def get_infos():
        return function_importer("./client/", "infos")

    @Slot(int)
    def on_gui_server_get_tasks(self, device_id):
        tasks = []
        for task in self.get_tasks():
            tasks.append({"name": task.__name__, "platforms": task.platforms,
                          "administrator": task.administrator, "kwargs": task.kwargs})
        self.available_tasks.emit(device_id, tasks)

    @Slot(int)
    def on_gui_server_get_infos(self, device_id):
        self.available_infos.emit(device_id, self.get_infos())

    @Slot(int)
    def on_gui_server_get_setup_options(self, device_id):
        resp = {}
        # keys
        resp["c2_key"] = generate_key().decode()
        resp["gui_key"] = generate_key().decode()

        # network interfaces
        interfaces = []
        for interface, snics in psutil.net_if_addrs().items():
            mac = None
            for snic in snics:
                if snic.family == -1:
                    mac = snic.address
                if snic.family == 2:
                    if mac:
                        interfaces.append({"ip": snic.address,
                                           "netmask": snic.netmask,
                                           "name": interface,
                                           "mac": mac})
        resp["interfaces"] = interfaces
        self.setup_options.emit(device_id, resp)

