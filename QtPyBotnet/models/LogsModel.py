from qtpy.QtCore import QObject

from logging import getLevelName


class Logs(QObject):

    def __init__(self, device, thread_name, name, level, msg, parent):
        super(Logs, self).__init__(parent)

        self.device = device
        self.thread_name = thread_name
        self.name = name
        self.level = level
        self.msg = msg

    def format(self):
        return "[Bot-{}] [{}] [{}] [{}] {}".format(self.level, self.thread_name, self.name,
                                                   getLevelName(self.level), self.msg)
