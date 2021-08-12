from qtpy.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit, QSpinBox, QPushButton, QDialogButtonBox, QVBoxLayout
from qtpy.QtCore import QSize, Qt, Signal, Slot

from qrainbowstyle.windows import FramelessWindow, FramelessWarningMessageBox
from qrainbowstyle.widgets import WaitingSpinner

from view.Windows import BaseFrame


class ServerAddressWidget(BaseFrame):
    connect_clicked = Signal(str, int, bytes)

    def __init__(self, parent):
        super(ServerAddressWidget, self).__init__(parent)

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.pass_widget = QWidget(self)
        self.pass_widget_layout = QFormLayout(self.pass_widget)
        self.pass_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.ip_label = QLabel(self.pass_widget)
        self.ip_label.setText("IP Address")

        self.ip_line_edit = QLineEdit(self.pass_widget)
        self.pass_widget_layout.addRow(self.ip_label, self.ip_line_edit)

        self.port_label = QLabel(self.pass_widget)
        self.port_label.setText("Port")

        self.port_edit = QSpinBox(self.pass_widget)
        self.port_edit.setRange(1024, 65535)
        self.pass_widget_layout.addRow(self.port_label, self.port_edit)

        self.key_label = QLabel(self.pass_widget)
        self.key_label.setText("Key")

        self.key_line_edit = QLineEdit(self.pass_widget)
        self.pass_widget_layout.addRow(self.key_label, self.key_line_edit)

        self.widget_layout.addWidget(self.pass_widget)

        self.connect_button = QPushButton(self)
        self.connect_button.clicked.connect(self.on_connect_clicked)
        self.connect_button.setMinimumSize(QSize(0, 35))
        self.connect_button.setText("Connect")
        self.widget_layout.addWidget(self.connect_button)

    @Slot()
    def on_connect_clicked(self):
        self.connect_clicked.emit(self.ip_line_edit.text(), self.port_edit.value(), self.key_line_edit.text().encode())
