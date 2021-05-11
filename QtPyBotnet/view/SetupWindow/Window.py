from qrainbowstyle.windows import FramelessWarningMessageBox, FramelessInformationMessageBox
from qtpy.QtWidgets import QPushButton, QDialogButtonBox
from qtpy.QtCore import Signal, QMetaObject, Slot, Qt

import logging

from view.BaseWidgets import BotnetWindow, FramesWidget
from view.SetupWindow.ConfigFrames import TermsFrame, ServerFrame, InfoFrame, FinishFrame, GUIFrame


class SetupDialog(BotnetWindow):
    accepted = Signal(dict)
    restart_accepted = Signal()
    cancelled = Signal()

    def __init__(self, parent=None):
        super(SetupDialog, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.warning_messagebox = None
        self.error_messagebox = None

        self.start_button = QPushButton("Start", self)
        self.start_button.setObjectName("start_button")
        self.start_button.setMinimumHeight(35)
        self.start_button.setVisible(True)
        self.addSubContentWidget(self.start_button)

        self.config_frame = FramesWidget(self)
        self.config_frame.add_frames([TermsFrame, GUIFrame, ServerFrame, InfoFrame, FinishFrame])

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
        self.warning_messagebox = FramelessWarningMessageBox(self)
        self.warning_messagebox.setWindowModality(Qt.WindowModal)
        self.warning_messagebox.setStandardButtons(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.warning_messagebox.button(QDialogButtonBox.No).clicked.connect(self.warning_messagebox.close)
        self.warning_messagebox.button(QDialogButtonBox.Yes).clicked.connect(self.cancelled.emit)
        self.warning_messagebox.setText("Do you really want to close setup dialog? Configuration will not be saved!")
        self.warning_messagebox.show()

    @Slot(str)
    def on_config_error(self, text: str):
        self.error_messagebox = FramelessWarningMessageBox(self)
        self.error_messagebox.setWindowModality(Qt.WindowModal)
        self.error_messagebox.setStandardButtons(QDialogButtonBox.Ok)
        self.error_messagebox.button(QDialogButtonBox.Ok).clicked.connect(self.error_messagebox.close)
        self.error_messagebox.setText(text)
        self.error_messagebox.show()

    @Slot()
    def on_first_setup_finished(self):
        self.success_messagebox = FramelessInformationMessageBox()
        self.success_messagebox.setWindowModality(Qt.WindowModal)
        self.success_messagebox.setStandardButtons(QDialogButtonBox.Ok)
        self.success_messagebox.button(QDialogButtonBox.Ok).clicked.connect(self.success_messagebox.close)
        self.success_messagebox.button(QDialogButtonBox.Ok).clicked.connect(self.restart_accepted.emit)
        self.success_messagebox.closeClicked.connect(self.restart_accepted.emit)
        self.success_messagebox.setText("Configration files has been successfully written to disk. "
                                        "Restart server app to continue.")
        self.success_messagebox.show()

    @Slot()
    def on_start_button_clicked(self):
        self.start_button.setVisible(False)
        self.config_frame.setVisible(True)

    @Slot()
    def close(self):
        if self.warning_messagebox:
            self.warning_messagebox.close()
        if self.error_messagebox:
            self.error_messagebox.close()
        super().close()
