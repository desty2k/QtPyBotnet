from qtpy.QtCore import (Slot, QSize)
from qtpy.QtWidgets import (QVBoxLayout, QLabel)

from .ConfigBaseFrame import ConfigBaseFrame


class FinishFrame(ConfigBaseFrame):

    def __init__(self, parent=None):
        super(FinishFrame, self).__init__(parent)
        self.setMinimumSize(QSize(0, 0))

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.finish_text = QLabel(self)
        self.finish_text.setWordWrap(True)
        self.finish_text.setText("Setup finished. Click finish button to send configuration to server. "
                                 "Happy hacking :)")
        self.widget_layout.addWidget(self.finish_text)

    @Slot()
    def collect_info(self):
        return {}
