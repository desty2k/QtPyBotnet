from qtpy.QtCore import QObject, Slot


class Module(QObject):
    """Represents loaded Python module."""

    def __init__(self, name, code, architecture, is_cross_platform=True):
        super(Module, self).__init__()
        self.name = name
        self.code = code
        self.architecture = architecture
        self.is_cross_platform = is_cross_platform

    @Slot()
    def serialize(self):
        return {"name": self.name, "code": self.code, "architecture": self.architecture,
                "is_cross_platform": self.is_cross_platform}

    @Slot(dict)
    def deserialize(self, module: dict):
        self.name = module.get("name")
        self.code = module.get("code", {})
        self.architecture = module.get("architecture")
        self.is_cross_platform = module.get("is_cross_platform")
