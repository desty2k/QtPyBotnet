from qtpy.QtWidgets import QTableView, QFrame, QAbstractScrollArea, QAbstractItemView, QTableWidget, QHeaderView
from qtpy.QtCore import Qt, Signal, QPoint, Slot, QModelIndex

from QtPyBotnet.models import Task


class QTable(QTableView):
    context_menu_requested = Signal(int)
    task_double_clicked = Signal(Task)

    def __init__(self, *args, **kwargs):
        super(QTable, self).__init__(*args, **kwargs)

        self.setAutoFillBackground(True)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.setGridStyle(Qt.SolidLine)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        self.horizontalHeader().setStretchLastSection(True)
        vheader = self.verticalHeader()
        vheader.setSortIndicatorShown(False)
        vheader.setVisible(False)

        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.customContextMenuRequested.connect(self.on_customContextMenuRequested)
        self.doubleClicked.connect(self.on_task_double_clicked)

    @Slot(QModelIndex)
    def on_task_double_clicked(self, index: QModelIndex):
        self.task_double_clicked.emit(self.model().getEventById(self.model().index(index.row(), 0).data()))

    @Slot(QPoint)
    def on_customContextMenuRequested(self, pos: QPoint):
        self.context_menu_requested.emit(int(self.model().index(self.rowAt(pos.y()), 0).data()))

    def setModel(self, model):
        super().setModel(model)
        for i in range(self.model().columnCount()):
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)


class ModulesTable(QTable):
    context_menu_requested = Signal(str)

    def __init__(self, *args, **kwargs):
        super(ModulesTable, self).__init__(*args, **kwargs)

    @Slot(QPoint)
    def on_customContextMenuRequested(self, pos: QPoint):
        self.context_menu_requested.emit(str(self.model().index(self.rowAt(pos.y()), 0).data()))


class TasksTable(QTable):
    context_menu_requested = Signal(int)

    def __init__(self, *args, **kwargs):
        super(TasksTable, self).__init__(*args, **kwargs)

    @Slot(QPoint)
    def on_customContextMenuRequested(self, pos: QPoint):
        self.context_menu_requested.emit(int(self.model().index(self.rowAt(pos.y()), 0).data()))
