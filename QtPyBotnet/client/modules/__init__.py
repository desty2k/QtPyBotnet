
class Module:
    """Base class for modules."""

    platforms = []
    description = __doc__
    administrator = {}
    experimental = False
    enabled = False

    def __init__(self):
        super(Module, self).__init__()
        self.name = ""

    def is_enabled(self):
        return self.__class__.enabled

    def serialize(self):
        return {"name": self.__class__.__name__,
                "enabled": self.is_enabled()}
