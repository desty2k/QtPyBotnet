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

        self.widget = QWidget(self)
        self.console_layout = QVBoxLayout(self.widget)
        self.widget.setLayout(self.console_layout)

        self._out_label = QLabel(self.widget)
        self._out_label.setText("Output")
        self.output = QTextEdit(self.widget)
        self.output.setReadOnly(True)
        self.highlighter = Highlighter(self.output.document())
        self.output.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.output.setTextColor(QColor(0, 255, 0))
        self.output.setFont(QFont(self.output.currentFont().family(), 10))

        self._in_label = QLabel(self.widget)
        self._in_label.setText("Command")
        self.input = QLineEdit(self.widget)
        self.input.setStyleSheet("background-color: rgb(0, 0, 0); color: rgb(0, 255, 0)")
        self.input.setFont(QFont(self.output.currentFont().family(), 10))

        self.sendButton = QPushButton(self.widget)
        self.sendButton.setObjectName("sendButton")
        self.sendButton.setText("Send command")

        self.console_layout.addWidget(self._out_label)
        self.console_layout.addWidget(self.output)
        self.console_layout.addWidget(self._in_label)
        self.console_layout.addWidget(self.input)
        self.console_layout.addWidget(self.sendButton)

        self.addContentWidget(self.widget)
        QMetaObject.connectSlotsByName(self)

    def on_sendButton_clicked(self):
        mess = self.input.text()
        try:
            mess = json.loads(mess)
            self.message.emit(mess)
            self.input.setText("")
            self.output.append("$: {}".format(mess))

        except json.JSONDecodeError as e:
            self.warn = FramelessCriticalMessageBox(self)
            self.warn.setText("Failed to convert string to JSON: {}".format(e))
            self.warn.setStandardButtons(QDialogButtonBox.Ok)
            self.warn.button(QDialogButtonBox.Ok).clicked.connect(self.warn.close)
            self.warn.show()

    def write(self, resp: dict):
        if resp.get("event_type"):
            resp = "[{}]: {}".format(str(resp.get("event_type")).upper(), resp)
        else:
            resp = str(resp)
        self.output.append(resp)
