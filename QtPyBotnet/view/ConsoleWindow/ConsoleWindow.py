from qtpy.QtCore import Signal, Qt, QMetaObject
from qtpy.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit, QDialogButtonBox
from qtpy.QtGui import QColor, QFont, QTextCharFormat, QSyntaxHighlighter

import json

from qrainbowstyle.windows import FramelessWindow, FramelessCriticalMessageBox


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super(Highlighter, self).__init__(parent)
        self.messageFormat = QTextCharFormat()
        self.messageFormat.setForeground(Qt.yellow)

        self.clientFormat = QTextCharFormat()
        self.clientFormat.setForeground(Qt.magenta)

        self.connectedFormat = QTextCharFormat()
        self.connectedFormat.setForeground(Qt.cyan)

        self.disconnectedFormat = QTextCharFormat()
        self.disconnectedFormat.setForeground(Qt.gray)

        self.errorFormat = QTextCharFormat()
        self.errorFormat.setForeground(Qt.red)

    def highlightBlock(self, text):
        if text.startswith('[TASK]'):
            self.setFormat(0, len(text), self.messageFormat)
        elif text.startswith('[MODULE]'):
            self.setFormat(0, len(text), self.clientFormat)
        elif text.startswith('[INFO]'):
            self.setFormat(0, len(text), self.disconnectedFormat)
        elif text.startswith('[CONNECTED]'):
            self.setFormat(0, len(text), self.connectedFormat)
        elif text.startswith('[ERROR]'):
            self.setFormat(0, len(text), self.errorFormat)


class Console(FramelessWindow):
    message = Signal(dict)

    def __init__(self, parent=None):
        super(Console, self).__init__(parent)

        self._widget = QWidget(self)
        self._console_layout = QVBoxLayout(self._widget)
        self._widget.setLayout(self._console_layout)

        self._out_label = QLabel(self._widget)
        self._out_label.setText("Output")
        self._output = QTextEdit(self._widget)
        self._output.setReadOnly(True)
        self.highlighter = Highlighter(self._output.document())
        self._output.setStyleSheet("background-color: rgb(0, 0, 0);")
        self._output.setTextColor(QColor(0, 255, 0))
        self._output.setFont(QFont(self._output.currentFont().family(), 10))

        self._in_label = QLabel(self._widget)
        self._in_label.setText("Command")
        self._input = QLineEdit(self._widget)
        self._input.setStyleSheet("background-color: rgb(0, 0, 0); color: rgb(0, 255, 0)")
        self._input.setFont(QFont(self._output.currentFont().family(), 10))

        self.sendButton = QPushButton(self._widget)
        self.sendButton.setObjectName("sendButton")
        self.sendButton.setText("Send command")

        self._console_layout.addWidget(self._out_label)
        self._console_layout.addWidget(self._output)
        self._console_layout.addWidget(self._in_label)
        self._console_layout.addWidget(self._input)
        self._console_layout.addWidget(self.sendButton)

        self.addContentWidget(self._widget)
        QMetaObject.connectSlotsByName(self)

    def on_sendButton_clicked(self):
        mess = self._input.text()
        try:
            mess = json.loads(mess)
            self.message.emit(mess)
            self._input.setText("")
            self._output.append("$: {}".format(mess))

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
        self._output.append(resp)
