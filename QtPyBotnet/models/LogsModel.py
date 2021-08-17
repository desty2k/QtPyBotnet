from qtpy.QtCore import QObject

from logging import getLevelName


class Log(QObject):

    def __init__(self, device_id, thread_name, name, level, msg):
        super(Log, self).__init__()

        self.device_id = device_id
        self.thread_name = thread_name
        self.name = name
        self.level = level
        self.msg = msg

    def format(self):
        return "[Bot-{}] [{}] [{}] [{}] {}".format(self.device_id, self.thread_name, self.name,
                                                   getLevelName(self.level), self.msg)

    def serialize(self):
        return {"event_type": "log", "device_id": self.device_id, "thread_name": self.thread_name,
                "name": self.name, "level": self.level, "msg": self.msg}

    @staticmethod
    def deserialize(data: dict):
        return Log(data.get("device_id"), data.get("thread_name"), data.get("name"), data.get("level"), data.get("msg"))
