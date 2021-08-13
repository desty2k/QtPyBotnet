from qtpy.QtWidgets import QMenu, QSystemTrayIcon, QStyle, QAction, QApplication
from qtpy.QtCore import Signal


class SystemTrayWidget(QSystemTrayIcon):
    show_action_triggered = Signal()
    hide_action_triggered = Signal()
    exit_action_triggered = Signal()

    def __init__(self, parent):
        super(SystemTrayWidget, self).__init__(parent)
        self.setIcon(QApplication.style().standardIcon(QStyle.SP_ComputerIcon))

        show_action = QAction("Show", self)
        exit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show_action_triggered.emit)
        hide_action.triggered.connect(self.hide_action_triggered.emit)
        exit_action.triggered.connect(self.exit_action_triggered.emit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(exit_action)
        self.setContextMenu(tray_menu)
