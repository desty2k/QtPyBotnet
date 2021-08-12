from qtpy.QtCore import Signal, Slot, Qt
from qtpy.QtGui import QSyntaxHighlighter, QTextCharFormat
from qtpy.QtWidgets import (QWidget, QPlainTextEdit, QLineEdit,
                            QPushButton, QVBoxLayout)

from models import Bot


class ShellHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super(ShellHighlighter, self).__init__(parent)
        self.input_format = QTextCharFormat()
        self.input_format.setForeground(Qt.red)

    def highlightBlock(self, text):
        if text.startswith('$: '):
            self.setFormat(0, len(text), self.input_format)


class ShellWidget(QWidget):
    run_shell = Signal(Bot, str)

    def __init__(self, bot, parent):
        super(ShellWidget, self).__init__(parent)
        self.bot = bot

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.output_widget = QPlainTextEdit(self)
        self.output_widget.setReadOnly(True)
        self.highlighter = ShellHighlighter(self.output_widget.document())
        self.widget_layout.addWidget(self.output_widget)

        self.input_widget = QLineEdit(self)
        self.widget_layout.addWidget(self.input_widget)

        self.send_button = QPushButton(self)
        self.send_button.setText("Send")
        self.send_button.clicked.connect(self.on_send_button_clicked)
        self.widget_layout.addWidget(self.send_button)

    @Slot()
    def on_send_button_clicked(self):
        text = self.input_widget.text()
        self.output_widget.appendPlainText("$: {}".format(text))
        self.run_shell.emit(self.bot, text)
        self.input_widget.clear()

    @Slot(Bot, str)
    def append_shell(self, bot, message):
        if self.bot == bot:
            self.output_widget.appendPlainText(message)
