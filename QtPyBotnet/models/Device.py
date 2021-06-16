from QtPyNetwork import models
from qtpy.QtCore import Slot


class Device(models.Device):

    def __init__(self, server, device_id, ip, port):
        super(Device, self).__init__(server, device_id, ip, port)
        self.verified = False
        self.key = None
        self.custom_key = None

    @Slot()
    def is_verified(self):
        return self.verified

    @Slot()
    def set_verified(self, value):
        self.verified = value

    @Slot(dict)
    def write(self, message: dict):
        self.server().write(self, message)
