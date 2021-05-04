from qtpy.QtWidgets import (QDialogButtonBox)
from qtpy.QtCore import (Signal, QMetaObject, Slot, Qt)

import logging

from qrainbowstyle.windows import FramelessCriticalMessageBox

from view.BaseWidgets import BotnetWindow
from view.LoginWindow.Frames import ConnectFrame, LoginFrame, ModeFrame


class LoginDialog(BotnetWindow):

    setup_relay = Signal()
    setup_server = Signal()
    setup_remote = Signal(str, int, str)
    setup_normal = Signal(str)

    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)

        self._connect_frame = ConnectFrame(self)
        self._mode_frame = ModeFrame(self)
        self._login_frame = LoginFrame(self)

        self.addSubContentWidget(self._connect_frame)
        self.addSubContentWidget(self._mode_frame)
        self.addSubContentWidget(self._login_frame)

        self._mode_frame.setVisible(True)
        self._connect_frame.setVisible(False)
        self._login_frame.setVisible(False)

        self._connect_frame.connect_clicked.connect(self.setup_remote.emit)
        self._login_frame.login_clicked.connect(self.setup_normal.emit)
        QMetaObject.connectSlotsByName(self)

    @Slot()
    def on_start_button_clicked(self):
        mode = self._mode_frame.mode_combo.currentIndex()
        if mode == 0:
            self._mode_frame.setVisible(False)
            self._login_frame.setVisible(True)
        elif mode == 1:
            self._mode_frame.setVisible(False)
            self._connect_frame.setVisible(True)
        elif mode == 2:
            self.setup_server.emit()
            self.hide()
        elif mode == 3:
            self.setup_relay.emit()
            self.hide()

    @Slot()
    def on_successfull_connection(self):
        self._connect_frame.on_successfull_connection()
        self.close()

    @Slot(str)
    def on_failed_login(self, text):
        self._connect_frame.on_failed_connection(text)

    @Slot()
    def on_successfull_login(self):
        self.close()
