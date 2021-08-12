from qtpy.QtCore import QObject, Slot

from datetime import datetime


class Module(QObject):
    """Represents loaded Python module.
    Code argument must be base64 encoded module code dumped with paker."""

    def __init__(self, name: str, code: bytes, architecture: str, cross_platform: bool = True, loaded: bool = False):
        super(Module, self).__init__()
        self.name = name
        self.code = code
        self.size = len(code)
        self.loaded = loaded
        self.architecture = architecture
        self.cross_platform = cross_platform

        if self.loaded:
            self.time_loaded = datetime.now()

    @Slot(bool)
    def set_loaded(self, value):
        self.loaded = value
        if value:
            self.time_loaded = datetime.now()

    @Slot()
    def create(self):
        return {"event_type": "module",
                "event": "load",
                "name": self.name,
                "code": self.code
                }

    @Slot()
    def serialize(self):
        return {"name": self.name,
                "code": self.code,
                "architecture": self.architecture,
                "cross_platform": self.cross_platform}

    @Slot(dict)
    def deserialize(self, module: dict):
        self.name = module.get("name")
        self.code = module.get("code", {})
        self.architecture = module.get("architecture")
        self.cross_platform = module.get("cross_platform")
