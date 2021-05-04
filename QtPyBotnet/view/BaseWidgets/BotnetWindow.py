from qtpy.QtGui import QFont
from qtpy.QtCore import Signal, Qt, QSize
from qtpy.QtWidgets import (QWidget, QGridLayout, QSizePolicy, QSpacerItem, QLabel)

import qrainbowstyle
from qrainbowstyle.windows import FramelessWindow


class BaseFrame(QWidget):

    def __init__(self, parent=None):
        super(BaseFrame, self).__init__(parent)
        self.setObjectName("botnet_frame_widget")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setStyleSheet(qrainbowstyle.rainbowize("""
                            BaseFrame {
                            border-radius: 3px;
                            border-color: COLOR_ACCENT_3;
                            border-width: 2px;
                            }
                        """))


class BotnetWindow(FramelessWindow):
    update_ui = Signal()

    def __init__(self, parent=None):
        super(BotnetWindow, self).__init__(parent)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(QSize(1500, 900))

        self.__mainWidget = QWidget(self)
        self.__mainWidget.setMouseTracking(True)
        self.__mainWidget.setAttribute(Qt.WA_TranslucentBackground)
        self.__mainWidget.setContentsMargins(0, 0, 0, 0)
        self.__gridLayout = QGridLayout(self.__mainWidget)
        self.__gridLayout.setContentsMargins(0, 0, 0, 0)
        self.__mainWidget.setLayout(self.__gridLayout)

        self.__spacerLeft = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.__gridLayout.addItem(self.__spacerLeft, 2, 1, 1, 1)

        self.__spacerTop = QSpacerItem(472, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.__gridLayout.addItem(self.__spacerTop, 1, 2, 1, 1)

        self.__spacerRight = QSpacerItem(472, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.__gridLayout.addItem(self.__spacerRight, 1, 0, 1, 1)

        self.__spacerBottom = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.__gridLayout.addItem(self.__spacerBottom, 0, 1, 1, 1)

        self.__subContentWidget = QWidget(self.__mainWidget)
        self.__subContentWidget.setMouseTracking(True)
        self.__subContentWidget.setContentsMargins(0, 0, 0, 0)
        self.__subContentLayout = QGridLayout(self.__subContentWidget)
        self.__subContentLayout.setContentsMargins(0, 0, 0, 0)
        self.__subContentWidget.setLayout(self.__subContentLayout)
        self.__subContentWidget.setAttribute(Qt.WA_TranslucentBackground)
        self.__gridLayout.addWidget(self.__subContentWidget, 1, 1, 1, 1)

        self.__nameSpacer = QSpacerItem(1, 16, QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.__subContentLayout.addItem(self.__nameSpacer, 1, 0, 1, 1)

        self.__app_name = QLabel(self)
        font = self.font()
        font.setPointSize(50)
        font.setWeight(QFont.Bold)
        self.__app_name.setFont(font)
        self.__app_name.setScaledContents(True)
        self.__app_name.setAutoFillBackground(True)
        self.__app_name.setAlignment(Qt.AlignCenter)
        self.__app_name.setText("QtPyBotnet")
        self.__app_name.setAttribute(Qt.WA_TranslucentBackground)
        self.__app_name.setScaledContents(True)
        self.__app_name.autoFillBackground()
        self.__subContentLayout.addWidget(self.__app_name, 0, 0, 1, 1)

        try:
            self.closeClicked.disconnect()
        except Exception:  # noqa
            pass

        self.setSubContentSpacing(16)
        self.addContentWidget(self.__mainWidget)

    def addSubContentWidget(self, widget: QWidget):
        self.__subContentLayout.addWidget(widget, 2, 0, 1, 1)

    def setSubContentSpacing(self, spacing: int):
        self.__subContentLayout.setSpacing(spacing)

    def showLogo(self, value: bool):
        self.__app_name.setVisible(value)
