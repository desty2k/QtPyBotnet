from qtpy.QtCore import Slot
from qtpy.QtWidgets import (QWidget, QFormLayout, QLabel, QHBoxLayout)

from models import Bot


class AttributesWidget(QWidget):
    """Shows info about device."""

    def __init__(self, bot, parent):
        super(AttributesWidget, self).__init__(parent)
        self.bot = bot

        self.widgets = []
        self.widget_layout = QHBoxLayout(self)
        self.setLayout(self.widget_layout)

        # widget with labels
        self.info_widget = QWidget(self)
        self.info_widget_layout = QFormLayout(self.info_widget)
        self.info_widget.setLayout(self.info_widget_layout)
        self.widget_layout.addWidget(self.info_widget)

        # widget with actions - remote shell, powershell, remote screen...
        self.actions_widget = QWidget(self)
        self.actions_widget_layout = QFormLayout(self.actions_widget)
        self.actions_widget.setLayout(self.actions_widget_layout)

    @Slot(Bot)
    def update_attributes(self, bot):
        # update labels with info about bot
        self.widgets.clear()
        for var, val in vars(bot).items():
            label = QLabel(self.info_widget)
            label.setText(" ".join(var.split("_")).capitalize())

            field = QLabel(self.info_widget)
            field.setText(str(val))
            self.widgets.append({"label": label, "field": field})
            self.info_widget_layout.addRow(label, field)
