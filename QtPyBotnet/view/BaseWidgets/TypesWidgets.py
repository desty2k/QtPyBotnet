from qtpy.QtWidgets import QWidget, QFormLayout, QLabel, QListView
from qtpy.QtGui import QStandardItemModel, QStandardItem


class StringDictWidget(QWidget):

    def __init__(self, parent):
        super(StringDictWidget, self).__init__(parent)
        self.widget_layout = QFormLayout(self)
        self.setLayout(self.widget_layout)

    def addEntry(self, key, value):
        key_label = QLabel(self)
        key_label.setText(str(key))

        value_label = QLabel(self)
        value_label.setText(str(value))
        self.widget_layout.addRow(key_label, value_label)


class StringListWidget(QListView):

    def __init__(self, parent):
        super(StringListWidget, self).__init__(parent)
        self.model = QStandardItemModel(self.list)
        self.setModel(self.model)

    def setData(self, data: list):
        for entry in data:
            item = QStandardItem(str(entry))
            self.model.appendRow(item)

    def addData(self, data: str):
        item = QStandardItem(str(data))
        self.model.appendRow(item)


class ListWidget(QWidget):

    def __init__(self, parent):
        super(ListWidget, self).__init__(parent)

