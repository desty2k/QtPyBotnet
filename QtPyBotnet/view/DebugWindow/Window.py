from qtpy.QtCore import Signal, Qt, QMetaObject
from qtpy.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit, QDialogButtonBox
from qtpy.QtGui import QColor, QFont, QTextCharFormat, QSyntaxHighlighter

import json

from qrainbowstyle.windows import FramelessWindow, FramelessCriticalMessageBox


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super(Highlighter, self).__init__(parent)
        self.taskFormat = QTextCharFormat()
        self.taskFormat.setForeground(Qt.yellow)

        self.infoFormat = QTextCharFormat()
        self.infoFormat.setForeground(Qt.gray)

        self.buildFormat = QTextCharFormat()
        self.buildFormat.setForeground(Qt.magenta)

        self.connectedFormat = QTextCharFormat()
        self.connectedFormat.setForeground(Qt.cyan)

        self.errorFormat = QTextCharFormat()
        self.errorFormat.setForeground(Qt.red)

    def highlightBlock(self, text):
        if text.startswith('[TASK]'):
            self.setFormat(0, len(text), self.taskFormat)
        elif text.startswith('[INFO]'):
            self.setFormat(0, len(text), self.infoFormat)
        elif text.startswith('[BUILD]'):
            self.setFormat(0, len(text), self.buildFormat)
        elif text.startswith('[CONNECTED]'):
            self.setFormat(0, len(text), self.connectedFormat)
        elif text.startswith('[ERROR]'):
            self.setFormat(0, len(text), self.errorFormat)


class Console(FramelessWindow):
    message = Signal(dict)

    def __init__(self, parent=None):
        super(Console, self).__init__(parent)
        self.json_decode_warning = None

        self.widget = QWidget(self)
        self.console_layout = QVBoxLayout(self.widget)
        self.widget.setLayout(self.console_layout)

        self.output_label = QLabel(self.widget)
        self.output_label.setText("Output")
        self.output_edit = QTextEdit(self.widget)
        self.output_edit.setReadOnly(True)
        self.highlighter = Highlighter(self.output_edit.document())
        self.output_edit.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.output_edit.setTextColor(QColor(0, 255, 0))
        self.output_edit.setFont(QFont(self.output_edit.currentFont().family(), 10))

        self.input_label = QLabel(self.widget)
        self.input_label.setText("Command")
        self.input_edit = QLineEdit(self.widget)
        self.input_edit.setStyleSheet("background-color: rgb(0, 0, 0); color: rgb(0, 255, 0)")
        self.input_edit.setFont(QFont(self.output_edit.currentFont().family(), 10))

        self.send_button = QPushButton(self.widget)
        self.send_button.setObjectName("send_button")
        self.send_button.setText("Send command")

        self.console_layout.addWidget(self.output_label)
        self.console_layout.addWidget(self.output_edit)
        self.console_layout.addWidget(self.input_label)
        self.console_layout.addWidget(self.input_edit)
        self.console_layout.addWidget(self.send_button)

        self.addContentWidget(self.widget)
        QMetaObject.connectSlotsByName(self)

    def on_send_button_clicked(self):
        mess = self.input_edit.text()
        try:
            mess = json.loads(mess)
            self.message.emit(mess)
            self.input_edit.clear()
            self.output_edit.append("$: {}".format(mess))

        except json.JSONDecodeError as e:
            self.json_decode_warning = FramelessCriticalMessageBox(self)
            self.json_decode_warning.setText("Failed to convert string to JSON: {}".format(e))
            self.json_decode_warning.setStandardButtons(QDialogButtonBox.Ok)
            self.json_decode_warning.button(QDialogButtonBox.Ok).clicked.connect(self.json_decode_warning.close)
            self.json_decode_warning.show()

    def write(self, resp: dict):
        if resp.get("event_type"):
            resp = "[{}]: {}".format(str(resp.get("event_type")).upper(), resp)
        else:
            resp = str(resp)
        self.output_edit.append(resp)
