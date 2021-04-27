from qtpy.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal

from models.Events import Info, Module, Task


class TableModel(QAbstractTableModel):
    removed = Signal(int)

    def __init__(self, parent=None):
        super(TableModel, self).__init__(parent)
        self.bots = []

        self.hheaders = [
            {"text": "ID", "contains": "id"},
            {"text": "Connected", "contains": "connected"},
            {"text": "IP address", "contains": "ip"},
            {"text": "Location", "contains": "geolocation"},
            {"text": "Architecture", "contains": "architecture"},
            {"text": "Username", "contains": "username"},
            {"text": "Administrator", "contains": "administrator"},
            {"text": "Language", "contains": "language"},
        ]

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.bots)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.hheaders)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if 0 <= index.row() < self.rowCount() and 0 <= index.column() < self.columnCount():
            if role == Qt.DisplayRole:
                data = getattr(self.bots[index.row()], self.hheaders[index.column()]["contains"])
                if data is None:
                    return "Unknown"
                elif type(data) is list:
                    data = ", ".join(data)
                return data

    def appendDevice(self, device):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.bots.append(device)
        self.endInsertRows()

    def updateDevice(self, bot_id, message):
        bot = self.getDeviceById(bot_id)
        event_type = message.get("event_type")
        if bot is not None and event_type is not None:
            if event_type == "task":
                event = Task(bot_id, message.get("task_id"),
                             message.get("task"),
                             message.get("state"),
                             message.get("result"),
                             message.get("exit_code"))
                bot.on_task_received(event)
            elif event_type == "info":
                event = Info(bot_id,
                             message.get("info"),
                             message.get("state"),
                             message.get("results"))
                bot.on_info_received(event)
            self.repaint()

    def removeDevice(self, bot_id):
        bot = self.getDeviceById(bot_id)
        if bot:
            self.bots.remove(bot)
            self.removed.emit(bot_id)
            self.repaint()

    def clear(self):
        """Clear the table"""
        self.beginResetModel()
        self.bots.clear()
        self.endResetModel()

    def repaint(self):
        """Update table when data changed"""
        self.beginResetModel()
        self.endResetModel()

    def getDevices(self):
        return self.bots

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.hheaders[section]["text"]

            elif orientation == Qt.Vertical:
                return section
        else:
            return None

    def getDeviceIndexById(self, bot_id):
        for bot in self.bots:
            if bot.get_id() == bot_id:
                return self.bots.index(bot)

    def getDeviceById(self, bot_id):
        for bot in self.bots:
            if bot.get_id() == bot_id:
                return bot
