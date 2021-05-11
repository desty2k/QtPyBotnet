from qtpy.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QCheckBox, QPushButton, QLineEdit, QComboBox,
                            QFormLayout, QLabel, QApplication, QSpinBox, QListView, QSizePolicy, QSpacerItem)
from qtpy.QtCore import (Signal, Qt, QMetaObject, Slot, QSize, QVariant)
from qtpy.QtGui import QTextOption, QStandardItemModel, QStandardItem

import os
import sys

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

    @Slot(dict)
    def set_options(self, options):
        pass


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


class GUIFrame(ConfigBaseFrame):

    def __init__(self, parent):
        super(GUIFrame, self).__init__(parent)
        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.gui_conf_label = QLabel(self)
        self.gui_conf_label.setText("GUI server configuration")
        self.widget_layout.addWidget(self.gui_conf_label)

        self.desc_label = QLabel(self)
        self.desc_label.setWordWrap(True)
        self.desc_label.setText("QtPyBotnet GUI if fully remote. This means that you can connect to C2 server and "
                                "manage bots wherever you are. To authenticate when connecting to GUI server use the "
                                "key below.")
        self.widget_layout.addWidget(self.desc_label)

        self.gui_config = QWidget(self)
        self.gui_config_layout = QFormLayout(self.gui_config)
        self.widget_layout.addWidget(self.gui_config)

        self.gui_ip_label = QLabel(self.gui_config)
        self.gui_ip_label.setObjectName("gui_ip_label")
        self.gui_ip_label.setText("GUI IP Address")

        self.gui_ip_combo = QComboBox(self.gui_config)
        self.gui_config_layout.addRow(self.gui_ip_label, self.gui_ip_combo)

        self.gui_port_label = QLabel(self.gui_config)
        self.gui_port_label.setObjectName("gui_port_label")
        self.gui_port_label.setText("GUI Port")

        self.gui_port_edit = QSpinBox(self.gui_config)
        self.gui_port_edit.setObjectName("gui_port_spin")
        self.gui_port_edit.setRange(1024, 65535)
        self.gui_port_edit.setValue(15692)
        self.gui_config_layout.addRow(self.gui_port_label, self.gui_port_edit)

        self.gui_key_label = QLabel(self.gui_config)
        self.gui_key_label.setObjectName("gui_key_label")
        self.gui_key_label.setText("GUI encryption key")

        self.gui_key_edit = QLineEdit(self.gui_config)
        self.gui_key_edit.setObjectName("gui_key_edit")
        self.gui_key_edit.setReadOnly(True)
        self.gui_config_layout.addRow(self.gui_key_label, self.gui_key_edit)

        self.gmaps_key_label = QLabel(self.gui_config)
        self.gmaps_key_label.setObjectName("gmaps_key_label")
        self.gmaps_key_label.setText("Google Maps API key")

        self.gmap_key_edit = QLineEdit(self.gui_config)
        self.gmap_key_edit.setObjectName("gmap_key_edit")
        self.gui_config_layout.addRow(self.gmaps_key_label, self.gmap_key_edit)

        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.widget_layout.addItem(spacerItem)

    @Slot(dict)
    def set_options(self, options):
        self.gui_ip_combo.addItems([iface.get("ip") for iface in options.get("interfaces")])
        self.gui_key_edit.setText(options.get("gui_key"))

    @Slot()
    def collect_info(self):
        return {"gui_ip": self.gui_ip_combo.currentText(),
                "gui_port": int(self.gui_port_edit.text()),
                "gmaps_key": self.gmap_key_edit.text(),
                "gui_key": self.gui_key_edit.text()}


class ServerFrame(ConfigBaseFrame):

    def __init__(self, parent):
        super(ServerFrame, self).__init__(parent)
        self._key = generate_key().decode()

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.c2_conf_label = QLabel(self)
        self.c2_conf_label.setText("C2 server configuration")
        self.widget_layout.addWidget(self.c2_conf_label)

        self.desc_label = QLabel(self)
        self.desc_label.setWordWrap(True)
        self.desc_label.setText("Make sure that port you use is opened and IP address is "
                                "valid. To balance server load, select amount of threads to use. Set 0 to use all "
                                "available system cores.")
        self.widget_layout.addWidget(self.desc_label)

        self.ip_config = QWidget(self)
        self.ip_config_layout = QFormLayout(self.ip_config)
        self.widget_layout.addWidget(self.ip_config)

        self.c2_ip_label = QLabel(self.ip_config)
        self.c2_ip_label.setText("C2 IP Address")

        self.c2_ip_combo = QComboBox(self.ip_config)
        self.ip_config_layout.addRow(self.c2_ip_label, self.c2_ip_combo)

        self.port_label = QLabel(self.ip_config)
        self.port_label.setText("C2 Port")

        self.port_edit = QSpinBox(self.ip_config)
        self.port_edit.setRange(1024, 65535)
        self.port_edit.setValue(8192)
        self.ip_config_layout.addRow(self.port_label, self.port_edit)

        self.threads_label = QLabel(self.ip_config)
        self.threads_label.setText("C2 handler threads")

        self.threads_edit = QSpinBox(self.ip_config)
        self.threads_edit.setRange(0, 256)
        self.ip_config_layout.addRow(self.threads_label, self.threads_edit)

        self.c2_key_label = QLabel(self.ip_config)
        self.c2_key_label.setText("C2 encryption key")

        self.c2_key_edit = QLineEdit(self.ip_config)
        self.c2_key_edit.setReadOnly(True)
        self.c2_key_edit.setText(self._key)
        self.ip_config_layout.addRow(self.c2_key_label, self.c2_key_edit)

        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.widget_layout.addItem(spacerItem)

    @Slot(dict)
    def set_options(self, options):
        self.c2_ip_combo.addItems([iface.get("ip") for iface in options.get("interfaces")])
        self.c2_key_edit.setText(options.get("c2_key"))

    @Slot()
    def collect_info(self):
        return {"c2_ip": self.c2_ip_combo.currentText(),
                "c2_port": int(self.port_edit.text()),
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

        self.item_string = {}
        infos = ConfigManager.get_infos()

        for info in infos:
            self.item_string[info] = {"name": " ".join(info.capitalize().split("_"))}

        for string in self.item_string:
            item = QStandardItem(self.item_string.get(string).get("name"))
            item.setFlags(Qt.ItemIsEnabled)
            item.setData(QVariant(Qt.Checked), Qt.CheckStateRole)
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
        self.finish_text.setText("Setup finished. Click finish button to send configuration to server. Happy hacking :)")
        self.widget_layout.addWidget(self.finish_text)

    @Slot()
    def collect_info(self):
        return {}
