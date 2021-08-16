from qtpy.QtWidgets import (QTextEdit, QVBoxLayout, QListWidget, QListWidgetItem)
from qtpy.QtCore import Slot


class LogsWidget(QTextEdit):
    """Widget with logs"""

    def __init__(self, bot, parent):
        super(LogsWidget, self).__init__(parent)
        self.bot = bot

        self.setReadOnly(True)
        self.clear()
        for log in self.bot.logs:
            self.append(str(log))

    @Slot(str)
    def append_log(self, log):
        self.append(str(log))
