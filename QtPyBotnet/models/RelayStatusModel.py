from qtpy.QtCore import Slot, QObject

from datetime import datetime

from models import Bot


class RelayStatus(QObject):

    def __init__(self, parent):
        super(RelayStatus, self).__init__(parent)
        self.active = False
        self.start_time = None

        self.ip = None
        self.port = None

        self.clients = []

    @Slot(str, int)
    def set_active(self, ip, port):
        self.start_time = datetime.now()
        self.active = True
        self.ip = ip
        self.port = port

    @Slot()
    def set_inactive(self):
        self.active = False
        self.ip = None
        self.port = None
        self.start_time = None
        self.clients.clear()

    @Slot()
    def is_active(self):
        return self.active

    @Slot(Bot)
    def bot_connected(self, bot: Bot):
        self.clients.append(bot)

    @Slot(Bot)
    def bot_disconnected(self, bot):
        if bot in self.clients:
            self.clients.remove(bot)
