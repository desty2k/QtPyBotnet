from qrainbowstyle.widgets import StylePickerHorizontal
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (QMenu, QAction, QWidgetAction)


class MainWindowMenu(QMenu):

    def __init__(self, parent):
        super(MainWindowMenu, self).__init__(parent)
        self.setTitle("QtPyBotnet")

        self.console_action = QAction('Show console', self)
        self.console_action.setObjectName("show_console")
        self.addAction(self.console_action)

        self.stay_top_action = QAction("Stay on top", self)
        self.stay_top_action.setObjectName("stay_top_action")
        self.stay_top_action.setCheckable(True)
        self.stay_top_action.setChecked(bool(self.window().windowFlags() & Qt.WindowStaysOnTopHint))
        self.addAction(self.stay_top_action)

        self.style_picker_action = QWidgetAction(self)
        self.style_picker = StylePickerHorizontal(self)
        self.style_picker_action.setDefaultWidget(self.style_picker)
        self.addAction(self.style_picker_action)
