from qtpy.QtWidgets import QWidget, QFormLayout, QTextEdit
from qrainbowstyle.windows import FramelessWindow

from models import Module

import base64


class ModuleDetailsWindow(FramelessWindow):

    def __init__(self, parent):
        super(ModuleDetailsWindow, self).__init__(parent)
        self.content_widget = QWidget(self)
        self.widget_layout = QFormLayout(self.content_widget)
        self.content_widget.setLayout(self.widget_layout)
        self.addContentWidget(self.content_widget)

        self.module_code = QTextEdit(self.content_widget)
        self.module_code.setReadOnly(True)
        self.widget_layout.addWidget(self.module_code)

    def set_module(self, module: Module):
        try:
            self.module_code.setText(base64.b64decode(module.code).decode())
        except Exception as e:
            self.module_code.setText("Exception while loading module's code: {}".format(e))
