from qtpy.QtWidgets import (QDialogButtonBox, QVBoxLayout, QWidget, QFrame, QRadioButton, QPushButton, QGroupBox,
                            QFormLayout, QLabel, QSpinBox, QCheckBox, QDateEdit)
from qtpy.QtCore import (Signal, QMetaObject, Slot, Qt, QDateTime)

from qrainbowstyle.windows import FramelessWindow

from view.TaskWindow.Widgets import MainTaskWidget


class TaskWindow(FramelessWindow):
    send_task = Signal(int, str)

    def __init__(self, parent):
        super(TaskWindow, self).__init__(parent)
        self.radios = []

        self.content_widget = MainTaskWidget(self)
        self.addContentWidget(self.content_widget)
