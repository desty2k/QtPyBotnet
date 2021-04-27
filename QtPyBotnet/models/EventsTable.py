from qtpy.QtCore import QAbstractTableModel, Qt, QModelIndex, Slot, QObject

import datetime

from models import Bot


class TasksTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super(TasksTableModel, self).__init__(parent)
        self.events = []
        self.hheaders = [
            {"text": "Task ID", "contains": "id"},
            {"text": "Task", "contains": "task"},
            {"text": "Time created", "contains": "time_created"},
            {"text": "Time started", "contains": "time_started"},
            {"text": "Time finished", "contains": "time_finished"},
            {"text": "User activity", "contains": "user_activity"},
            {"text": "State", "contains": "state"},
            {"text": "Result", "contains": "result"},
            {"text": "Exit code", "contains": "exit_code"},
        ]

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.events)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.hheaders)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if 0 <= index.row() < self.rowCount() and 0 <= index.column() < self.columnCount():
            if role == Qt.DisplayRole:
                data = getattr(self.events[index.row()], self.hheaders[index.column()]["contains"])
                if data is None:
                    return "Unknown"
                elif type(data) is dict:
                    if data.get("type") == "images":
                        data = "Images (Click to view)"
                    else:
                        data = "Dictionary (Click to view)"
                elif type(data) is list:
                    data = "List (Click to view)"
                elif type(data) is datetime.datetime:
                    data = data.strftime("%Y-%m-%d %H:%M:%S")
                return data

    @Slot(Bot)
    def setBot(self, bot):
        bot.updated.connect(self.update)
        self.events = bot.tasks

    @Slot()
    def clear(self):
        """Clear the table"""
        self.beginResetModel()
        self.events.clear()
        self.endResetModel()

    @Slot()
    def update(self):
        """Update table when data changed"""
        self.beginResetModel()
        self.endResetModel()

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.hheaders[section]["text"]

            elif orientation == Qt.Vertical:
                return section

    def getEventIndexById(self, event_id):
        for event in self.events:
            if event.get_id() == event_id:
                return self.events.index(event)

    def getEventById(self, event_id):
        for event in self.events:
            if event.get_id() == event_id:
                return event
