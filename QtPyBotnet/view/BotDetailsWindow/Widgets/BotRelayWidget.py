from qtpy.QtWidgets import (QWidget, QVBoxLayout, QLabel)


class RelayWidget(QWidget):
    """Widget with relay status and table with connected bots."""

    def __init__(self, bot, parent):
        super(RelayWidget, self).__init__(parent)
        self.bot = bot

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.relay_status = QLabel(self)
        self.widget_layout.addWidget(self.relay_status)
        if self.bot.relay_status is None:
            self.relay_status.setText("Inactive")
        else:
            self.relay_status.setText("Active")
