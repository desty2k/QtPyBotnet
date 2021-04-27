from qtpy.QtCore import QAbstractTableModel, Qt, QModelIndex, Slot, QObject

import datetime


class EventsTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super(EventsTableModel, self).__init__(parent)
        self.events = []
        self.hheaders = []

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

    @Slot(list)
    def setEvents(self, events_table):
        self.events = events_table
        self.update()

    @Slot(QObject)
    def addEvent(self, event):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.events.append(event)
        self.endInsertRows()

    @Slot(list)
    def addEvents(self, events):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        for event in events:
            event.updated.connect(self.update)
            self.events.append(event)
        self.endInsertRows()
        self.update()

    def updateEvent(self, event_id, task):
        event_id = self.getEventIndexById(event_id)
        self.getEventIndexById(event_id).update(task)
        self.update()

    @Slot(int)
    def removeEvent(self, event_id):
        self.events.remove(self.getEventById(event_id))
        self.update()

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


class TasksTableModel(EventsTableModel):

    def __init__(self, parent=None):
        super(TasksTableModel, self).__init__(parent)
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


class InfosTableModel(EventsTableModel):

    def __init__(self, parent=None):
        super(InfosTableModel, self).__init__(parent)
        self.hheaders = [
            {"text": "Info", "contains": "info"},
            {"text": "Time", "contains": "time_created"},
            {"text": "State", "contains": "state"},
            {"text": "Results", "contains": "results"},
        ]
