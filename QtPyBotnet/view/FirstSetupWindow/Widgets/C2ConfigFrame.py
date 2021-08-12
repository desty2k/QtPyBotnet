from qtpy.QtCore import (Slot)
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QComboBox,
                            QFormLayout, QLabel, QSpinBox, QSizePolicy, QSpacerItem)

from core.crypto import generate_key

from .ConfigBaseFrame import ConfigBaseFrame


class C2ConfigFrame(ConfigBaseFrame):

    def __init__(self, parent):
        super(C2ConfigFrame, self).__init__(parent)

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
        self.c2_key_edit.setText(generate_key().decode())
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
                "c2_key": str(self.c2_key_edit.text())}
