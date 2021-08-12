from qtpy.QtCore import (Qt, QMetaObject, Slot)
from qtpy.QtGui import QTextOption
from qtpy.QtWidgets import (QVBoxLayout, QTextEdit, QCheckBox)

import os
import sys

from .ConfigBaseFrame import ConfigBaseFrame


class TermsFrame(ConfigBaseFrame):

    def __init__(self, parent=None):
        super(TermsFrame, self).__init__(parent)
        self.setObjectName("botnet_termsframe_start")
        self.disable_next_on_enter = True

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.terms = QTextEdit(self)
        self.terms.setReadOnly(True)
        self.terms.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.terms.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.terms.setLineWrapMode(QTextEdit.WidgetWidth)
        self.terms.setWordWrapMode(QTextOption.WrapAnywhere)
        with open(os.path.join(sys.path[0], "../LICENSE")) as f:
            self.terms.setText(f.read())
        self.widget_layout.addWidget(self.terms)

        self.accept = QCheckBox(self)
        self.accept.setChecked(False)
        self.accept.setText("Accept license")
        self.accept.setObjectName("license_checkbox")
        self.widget_layout.addWidget(self.accept)

        QMetaObject.connectSlotsByName(self)

    @Slot(bool)
    def on_license_checkbox_clicked(self, checked):
        self.set_next_enabled.emit(checked)
        self.disable_next_on_enter = not checked

    @Slot()
    def collect_info(self):
        return {"terms_accepted": self.accept.isChecked()}
