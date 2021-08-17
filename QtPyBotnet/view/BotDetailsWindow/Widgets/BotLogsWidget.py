from qtpy.QtWidgets import (QTextEdit, QVBoxLayout, QListWidget, QListWidgetItem)
from qtpy.QtCore import Slot


class LogsWidget(QTextEdit):
    """Widget with logs"""

    def __init__(self, bot, parent):
        super(LogsWidget, self).__init__(parent)
        self.bot = bot
        self.bot.updated.connect(self.on_bot_updated)

        self.setReadOnly(True)
        self.on_bot_updated()

    @Slot()
    def on_bot_updated(self):
        self.clear()
        for log in self.bot.logs:
            self.append(str(log.format()))

    @Slot(str)
    def append_log(self, log):
        self.append(str(log))
