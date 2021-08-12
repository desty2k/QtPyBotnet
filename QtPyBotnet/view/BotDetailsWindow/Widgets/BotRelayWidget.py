from qtpy.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem)


class RelayWidget(QWidget):
    """Widget with relay status and table with connected bots."""

    def __init__(self, bot, parent):
        super(RelayWidget, self).__init__(parent)
        self.bot = bot

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.modules_list = QListWidget(self)
        self.widget_layout.addWidget(self.modules_list)

        for module in bot.modules:
            self.modules_list.addItem(QListWidgetItem(module.name, self.modules_list))
