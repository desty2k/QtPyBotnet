from qtpy.QtCore import QAbstractTableModel, Qt, Slot

import datetime

from models import Bot


class ModulesTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super(ModulesTableModel, self).__init__(parent)
        self.modules = []
        self.horizontal_headers = [
            {"text": "Name", "contains": "name"},
            {"text": "Architecture", "contains": "architecture"},
            {"text": "Time loaded", "contains": "time_loaded"},
            {"text": "Size (bytes)", "contains": "size"},
            {"text": "Cross-platform", "contains": "cross_platform"},
        ]

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.modules)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.horizontal_headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if 0 <= index.row() < self.rowCount() and 0 <= index.column() < self.columnCount():
            if role == Qt.DisplayRole:
                data = getattr(self.modules[index.row()], self.horizontal_headers[index.column()]["contains"])
                if data is None:
                    return "Unknown"
                elif type(data) is datetime.datetime:
                    data = data.strftime("%Y-%m-%d %H:%M:%S")
                return data

    @Slot(Bot)
    def setBot(self, bot):
        bot.updated.connect(self.update)
        self.modules = bot.modules

    @Slot()
    def clear(self):
        """Clear the table"""
        self.beginResetModel()
        self.modules.clear()
        self.endResetModel()

    @Slot()
    def update(self):
        """Update table when data changed"""
        self.beginResetModel()
        self.endResetModel()

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.horizontal_headers[section]["text"]

            elif orientation == Qt.Vertical:
                return section

    def getModuleByName(self, module_name):
        for module in self.modules:
            if module.name == module_name:
                return module
