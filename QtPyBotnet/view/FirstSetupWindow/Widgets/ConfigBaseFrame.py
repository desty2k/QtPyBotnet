from qtpy.QtWidgets import QWidget
from qtpy.QtCore import Signal, Slot, QSize


class ConfigBaseFrame(QWidget):
    accepted = Signal()
    rejected = Signal()
    set_next_enabled = Signal(bool)

    def __init__(self, parent=None):
        super(ConfigBaseFrame, self).__init__(parent)
        self.setMinimumSize(QSize(800, 500))
        self.disable_next_on_enter = False

    @Slot(dict)
    def set_options(self, options):
        pass
