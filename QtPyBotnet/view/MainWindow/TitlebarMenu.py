from qtpy.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTableView, QFrame, QAbstractItemView,
                            QTableWidget, QSizePolicy, QAbstractScrollArea, QHeaderView, QMenu, QAction)
from qtpy.QtCore import QSize, Qt


class TitlebarMenu(QMenu):

    def __init__(self, parent):
        super(TitlebarMenu, self).__init__(parent)
        self.setTitle("QtPyBotnet")

        self.console_action = QAction('Show console', self)
        self.console_action.setObjectName("show_console")
        self.addAction(self.console_action)

        self.style_action = QAction('Change style', self)
        self.style_action.setObjectName("change_style")
        self.addAction(self.style_action)

        self.stay_top_action = QAction("Stay on top", self)
        self.stay_top_action.setObjectName("stay_top_action")
        self.stay_top_action.setCheckable(True)
        self.stay_top_action.setChecked(bool(self.window().windowFlags() & Qt.WindowStaysOnTopHint))
        self.addAction(self.stay_top_action)
