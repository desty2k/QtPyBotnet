from qtpy.QtCore import Qt, Slot, Signal
from qtpy.QtWidgets import QDialogButtonBox

from qrainbowstyle.widgets import WaitingSpinner
from qrainbowstyle.windows import FramelessWarningMessageBox

from view.Windows import BotnetWindow
from .Widgets import ServerAddressWidget


class RemoteConnectWindow(BotnetWindow):
    """Dialog used to connect to GUI server."""
    connect_clicked = Signal(str, int, bytes)

    def __init__(self, parent=None):
        super(RemoteConnectWindow, self).__init__(parent)
        self.message_box = None

        self.sub_widget = ServerAddressWidget(self)
        self.sub_widget.connect_clicked.connect(self.on_connect_clicked)
        self.addSubContentWidget(self.sub_widget)

        self.spinner = WaitingSpinner(self, centerOnParent=True, roundness=70.0, fade=70.0, radius=15.0, lines=6,
                                      line_length=25.0, line_width=4.0, speed=1.0,
                                      disableParentWhenSpinning=True, modality=Qt.WindowModal)

    @Slot()
    def on_gui_client_connected(self):
        self.spinner.stop()
        self.close()

    @Slot()
    def on_gui_client_failed_to_connect(self):
        self.sub_widget.setEnabled(True)
        self.spinner.stop()
        self.message_box = FramelessWarningMessageBox(self)
        self.message_box.setWindowModality(Qt.WindowModal)
        self.message_box.setStandardButtons(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.message_box.button(QDialogButtonBox.No).clicked.connect(self.closeClicked.emit)
        self.message_box.setText("Failed to connect to GUI server. Do you want to retry?")
        self.message_box.show()

    @Slot(str, int, bytes)
    def on_connect_clicked(self, ip, port, key):
        self.sub_widget.setEnabled(False)
        self.spinner.start()
        self.connect_clicked.emit(ip, port, key)
