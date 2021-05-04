import os
import json
import logging

from qtpy.QtCore import Signal, QObject, Slot

from core.crypto import encrypt, decrypt
from core.importer import get_subclassess_by_name, function_importer


class ConfigManager(QObject):
    """Manages and loads config files."""
    config_created = Signal()
    config_error = Signal(str)
    config_read = Signal(dict)
    config_read_error = Signal(str)

    available_tasks = Signal(int, list)
    available_infos = Signal(int, list)

    def __init__(self):
        super(ConfigManager, self).__init__(None)
        self.__config = {}
        self.__key = ""
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__config_path = os.path.expanduser("~\\QtPyBotnet.cfg")

    def setValue(self, key, value):
        if self.__config_path:
            self.__config[key] = value
        else:
            raise Exception("Config not loaded")

    def value(self, key):
        if self.__config_path:
            return self.__config.get(key)
        else:
            raise Exception("Config not loaded")

    def sync(self):
        with open(self.__config_path, "w+") as f:
            data = json.dumps(self.__config)
            data = encrypt(data.encode(), self.__key.encode()).decode()
            f.write(data)
            self.__logger.info("Config written in {}".format(self.__config_path))

    def config_exists(self):
        return os.path.exists(self.__config_path) and os.path.isfile(self.__config_path)

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
    def on_gui_client_get_tasks(self, device_id):
        tasks = []
        for task in self.get_tasks():
            tasks.append({"name": task.__name__, "platforms": task.platforms,
                          "administrator": task.administrator, "kwargs": task.kwargs})
        self.available_tasks.emit(device_id, tasks)

    @Slot(int)
    def on_gui_client_get_infos(self, device_id):
        self.available_infos.emit(device_id, self.get_infos())

    def create(self, config, key: str):
        try:
            with open(self.__config_path, "w+") as f:
                data = json.dumps(config)
                data = encrypt(data.encode(), key.encode()).decode()
                f.write(data)
            self.config_created.emit()
            self.__logger.info("Config written in {}".format(self.__config_path))
        except Exception as e:
            self.config_error.emit("Failed to create config: {}".format(e))

    def load(self, key: str) -> dict:
        key = key.encode()
        if self.config_exists():
            data = open(self.__config_path, "r").read().encode()
            try:
                data = decrypt(data, key).decode()
                if data:
                    self.__config = json.loads(data)
                    self.config_read.emit(self.__config)
                    return self.__config
                else:
                    self.config_error.emit("Invalid config file.")
            except json.JSONDecodeError:
                self.config_error.emit("Config is not valid JSON.")
            except ValueError:
                self.config_error.emit("Invalid decryption key!")
            except Exception as e:
                self.config_error.emit("Failed to decrypt config file: {}".format(e))
        else:
            self.config_error.emit("Could not find config file.")
