from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap, QStandardItem, QStandardItemModel
from qtpy.QtWidgets import QWidget, QFormLayout, QLabel, QScrollArea, QHBoxLayout, QListView

from base64 import b64decode


class StringDictWidget(QWidget):
    """Show dict in key-value form."""

    def __init__(self, parent):
        super(StringDictWidget, self).__init__(parent)
        self.setContentsMargins(11, 11, 11, 11)
        self.widget_layout = QFormLayout(self)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.widget_layout)

    def addEntry(self, key, value):
        key_label = QLabel(self)
        key_label.setText(str(key))

        value_label = QLabel(self)
        value_label.setText(str(value))
        self.widget_layout.addRow(key_label, value_label)


class PixmapGallery(QScrollArea):
    """Display multiple pixmaps in one widget with scroll bars."""

    def __init__(self, parent):
        super(PixmapGallery, self).__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.labels = []
        self.widget_layout = QHBoxLayout(self)
        self.setLayout(self.widget_layout)

    def addFromBase64(self, data):
        data = b64decode(data)
        label = QLabel(self)
        label.setScaledContents(True)
        self.labels.append(label)
        self.widget_layout.addWidget(label)

        pix = QPixmap()
        pix.loadFromData(data, "PNG")
        pix.scaled(label.width(), label.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        label.setPixmap(pix)


class StringListWidget(QListView):
    """Display list of strings."""

    def __init__(self, parent):
        super(StringListWidget, self).__init__(parent)
        self.model = QStandardItemModel(self)
        self.setModel(self.model)

    def setData(self, data: list):
        for entry in data:
            item = QStandardItem(str(entry))
            self.model.appendRow(item)

    def addData(self, data: str):
        item = QStandardItem(str(data))
        self.model.appendRow(item)
