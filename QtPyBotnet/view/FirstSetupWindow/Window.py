from qrainbowstyle.windows import FramelessWarningMessageBox, FramelessInformationMessageBox
from qtpy.QtWidgets import QPushButton, QDialogButtonBox
from qtpy.QtCore import Signal, QMetaObject, Slot, Qt

import logging

from view.Windows import BotnetWindow
from view.Widgets import FramesWidget

from .Widgets import TermsFrame, C2ConfigFrame, InfoFrame, FinishFrame, GUIConfigFrame


class SetupDialog(BotnetWindow):
    accepted = Signal(dict)
    restart_accepted = Signal()
    cancelled = Signal()

    def __init__(self, parent=None):
        super(SetupDialog, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.message_box = None

        self.start_button = QPushButton("Start", self)
        self.start_button.setObjectName("start_button")
        self.start_button.setMinimumHeight(35)
        self.start_button.setVisible(True)
        self.addSubContentWidget(self.start_button)

        self.config_frame = FramesWidget(self)
        self.config_frame.add_frames([TermsFrame, GUIConfigFrame, C2ConfigFrame, InfoFrame, FinishFrame])

        self.config_frame.setObjectName("config_frame")
        self.config_frame.setVisible(False)
        self.addSubContentWidget(self.config_frame)

        QMetaObject.connectSlotsByName(self)
        try:
            self.closeClicked.disconnect()
        except Exception:
            pass
        self.closeClicked.connect(self.on_config_frame_rejected)

    @Slot(dict)
    def set_options(self, options):
        self.config_frame.set_options(options)

    @Slot()
    def on_config_frame_accepted(self):
        self.accepted.emit(self.config_frame.collect_info())

    @Slot()
    def on_config_frame_back(self):
        self.config_frame.setVisible(False)
        self.start_button.setVisible(True)

    @Slot()
    def on_config_frame_rejected(self):
        self.message_box = FramelessWarningMessageBox(self)
        self.message_box.setWindowModality(Qt.WindowModal)
        self.message_box.setStandardButtons(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.message_box.button(QDialogButtonBox.No).clicked.connect(self.message_box.close)
        self.message_box.button(QDialogButtonBox.Yes).clicked.connect(self.cancelled.emit)
        self.message_box.setText("Do you really want to close setup dialog? Configuration will not be saved!")
        self.message_box.show()

    @Slot(str)
    def on_config_error(self, text: str):
        self.message_box = FramelessWarningMessageBox(self)
        self.message_box.setWindowModality(Qt.WindowModal)
        self.message_box.setStandardButtons(QDialogButtonBox.Ok)
        self.message_box.button(QDialogButtonBox.Ok).clicked.connect(self.message_box.close)
        self.message_box.setText(text)
        self.message_box.show()

    @Slot()
    def on_first_setup_finished(self):
        self.message_box = FramelessInformationMessageBox()
        self.message_box.setWindowModality(Qt.WindowModal)
        self.message_box.setStandardButtons(QDialogButtonBox.Ok)
        self.message_box.button(QDialogButtonBox.Ok).clicked.connect(self.message_box.close)
        self.message_box.button(QDialogButtonBox.Ok).clicked.connect(self.restart_accepted.emit)
        self.message_box.closeClicked.connect(self.restart_accepted.emit)
        self.message_box.setText("Configration files has been successfully written to disk. "
                                        "Restart server app to continue.")
        self.message_box.show()

    @Slot()
    def on_start_button_clicked(self):
        self.start_button.setVisible(False)
        self.config_frame.setVisible(True)

    @Slot()
    def close(self):
        if self.message_box:
            self.message_box.close()
        super().close()
