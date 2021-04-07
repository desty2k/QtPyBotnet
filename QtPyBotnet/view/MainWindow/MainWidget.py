import os
import sys

from qtpy.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTableView, QFrame, QAbstractItemView,
                            QTableWidget, QSizePolicy, QAbstractScrollArea, QHeaderView)
from qtpy.QtCore import QSize, Qt, Slot, QModelIndex, Signal
from qtpy.QtGui import QIcon

from qrainbowstyle.widgets import GoogleMapsView

from QtPyBotnet.models import Bot
from QtPyBotnet.models.BotTable import TableModel


class MainWidget(QWidget):
    bot_double_clicked = Signal(Bot)
    task_button_clicked = Signal()
    payload_button_clicked = Signal()
    bot_clicked = Signal(int)

    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)
        self.mainLayout = QHBoxLayout(self)
        self.setLayout(self.mainLayout)

    def setupUi(self, config):
        self.sessionsWidget = QWidget(self)
        self.sessionsWidget.setContentsMargins(0, 0, 0, 0)
        self.sessionsWidgetLayout = QVBoxLayout(self.sessionsWidget)
        self.sessionsWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.sessionsWidget.setLayout(self.sessionsWidgetLayout)
        self.mainLayout.addWidget(self.sessionsWidget)

        self.map = GoogleMapsView(self.sessionsWidget, config.value("gmaps_key"))
        self.map.getHandler().markerDoubleClicked.connect(lambda bot_id, lat, lng: self.bot_double_clicked.emit(
            self.tableModel.getDeviceById(int(bot_id))))
        self.map.getHandler().markerClicked.connect(self.bot_clicked.emit)

        self.map.setObjectName("mapWidget")
        self.map.enableMarkersDragging(False)
        self.sessionsWidgetLayout.addWidget(self.map)

        self.botsTable = QTableView(self.sessionsWidget)
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
        self.botsTable.setMaximumHeight(200)
        self.tableModel = TableModel(self)
        self.tableModel.setObjectName("tableModel")
        self.tableModel.removed.connect(self.map.deleteMarker)
        self.botsTable.setModel(self.tableModel)

        for i in range(self.tableModel.columnCount()):
            self.botsTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.sessionsWidgetLayout.addWidget(self.botsTable)

        self.separatorLine = QFrame(self)
        self.separatorLine.setFrameShape(QFrame.VLine)
        self.separatorLine.setFrameShadow(QFrame.Sunken)

        sizepolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizepolicy.setHorizontalStretch(0)
        sizepolicy.setVerticalStretch(0)

        self.buttonsWidget = QWidget(self)
        self.buttonsWidget.setContentsMargins(0, 0, 0, 0)
        self.buttonsWidget.setSizePolicy(sizepolicy)
        self.buttonsWidgetLayout = QVBoxLayout(self.buttonsWidget)
        self.buttonsWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonsWidget.setLayout(self.buttonsWidgetLayout)

        btn_size = QSize(50, 50)

        self.btn0 = QPushButton(self.buttonsWidget)
        self.btn0.setToolTip("Create payload")
        self.btn0.setSizePolicy(sizepolicy)
        self.btn0.setMinimumSize(btn_size)
        self.btn0.setIconSize(self.btn0.size())
        self.btn0.clicked.connect(self.payload_button_clicked.emit)
        self.btn0.setIcon(QIcon(os.path.join(sys.path[0], "resources/icons/3d-cube-sphere.svg")))

        self.btn1 = QPushButton(self.buttonsWidget)
        self.btn1.setToolTip("Send task")
        self.btn1.setSizePolicy(sizepolicy)
        self.btn1.setMinimumSize(btn_size)
        self.btn1.setIconSize(self.btn0.size())
        self.btn1.clicked.connect(self.task_button_clicked.emit)
        self.btn1.setIcon(QIcon(os.path.join(sys.path[0], "resources/icons/list-check.svg")))

        # self.btn2 = QPushButton(self.buttonsWidget)
        # self.btn2.setToolTip("Send module")
        # self.btn2.setSizePolicy(sizepolicy)
        # self.btn2.setMinimumSize(btn_size)
        # self.btn2.setIconSize(self.btn0.size())
        # self.btn2.clicked.connect(lambda: self.button_clicked.emit("module"))
        # self.btn2.setIcon(QIcon(os.path.join(sys.path[0], "resources/icons/apps.svg")))
        #
        # self.btn3 = QPushButton(self.buttonsWidget)
        # self.btn3.setToolTip("Disconnect")
        # self.btn3.setSizePolicy(sizepolicy)
        # self.btn3.setMinimumSize(btn_size)
        # self.btn3.setIconSize(self.btn0.size())
        # self.btn3.clicked.connect(lambda: self.button_clicked.emit("disconnect"))
        # self.btn3.setIcon(QIcon(os.path.join(sys.path[0], "resources/icons/wifi.svg")))
        #
        # self.btn4 = QPushButton(self.buttonsWidget)
        # self.btn4.setToolTip("Kill all")
        # self.btn4.setSizePolicy(sizepolicy)
        # self.btn4.setMinimumSize(btn_size)
        # self.btn4.setIconSize(self.btn0.size())
        # self.btn4.clicked.connect(lambda: self.button_clicked.emit("kill"))
        # self.btn4.setIcon(QIcon(os.path.join(sys.path[0], "resources/icons/bolt.svg")))
        #
        # self.btn5 = QPushButton(self.buttonsWidget)
        # self.btn5.setToolTip("Close")
        # self.btn5.setSizePolicy(sizepolicy)
        # self.btn5.setMinimumSize(btn_size)
        # self.btn5.setIconSize(self.btn0.size())
        # self.btn5.clicked.connect(lambda: self.button_clicked.emit("close"))
        # self.btn5.setIcon(QIcon(os.path.join(sys.path[0], "resources/icons/alert-circle.svg")))

        self.buttonsWidgetLayout.addWidget(self.btn0)
        self.buttonsWidgetLayout.addWidget(self.btn1)
        # self.buttonsWidgetLayout.addWidget(self.btn2)
        # self.buttonsWidgetLayout.addWidget(self.btn3)
        # self.buttonsWidgetLayout.addWidget(self.btn4)
        # self.buttonsWidgetLayout.addWidget(self.btn5)

        self.mainLayout.addWidget(self.sessionsWidget)
        self.mainLayout.addWidget(self.separatorLine)
        self.mainLayout.addWidget(self.buttonsWidget)

    @Slot(QModelIndex)
    def on_botTable_doubleClicked(self, index: QModelIndex):
        self.bot_double_clicked.emit(self.tableModel.getDeviceById(self.tableModel.index(index.row(), 0).data()))

    def add_bot(self, bot_id, ip, port, kwargs={}):
        bot = Bot(bot_id, ip, port, **kwargs)
        bot.update_map.connect(lambda marker_id, loc: self.map.addMarker(marker_id, loc[0], loc[1]))
        self.tableModel.appendDevice(bot)

    def update_bot(self, bot_id, kwargs):
        self.tableModel.updateDevice(bot_id, kwargs)

    def remove_bot(self, bot_id):
        self.tableModel.removeDevice(bot_id)
