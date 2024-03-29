from qtpy.QtWidgets import QTableView, QFrame, QAbstractScrollArea, QAbstractItemView, QTableWidget, QHeaderView
from qtpy.QtCore import Qt, Signal, QPoint, Slot, QModelIndex

from models import Module


class ModulesTableView(QTableView):
    context_menu_requested = Signal(str)
    module_double_clicked = Signal(Module)

    def __init__(self, *args, **kwargs):
        super(ModulesTableView, self).__init__(*args, **kwargs)

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
        self.doubleClicked.connect(self.on_module_double_clicked)

    @Slot(QModelIndex)
    def on_module_double_clicked(self, index: QModelIndex):
        self.module_double_clicked.emit(self.model().getModuleByName(self.model().index(index.row(), 0).data()))

    @Slot(QPoint)
    def on_customContextMenuRequested(self, pos: QPoint):
        item = self.model().index(self.rowAt(pos.y()), 0).data()
        try:
            item = str(item)
            self.context_menu_requested.emit(item)
        except ValueError:
            pass

    def setModel(self, model):
        super().setModel(model)
        for i in range(self.model().columnCount()):
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
