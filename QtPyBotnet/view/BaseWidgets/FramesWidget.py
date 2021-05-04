from qtpy.QtWidgets import (QWidget, QVBoxLayout, QDialogButtonBox, QGridLayout)
from qtpy.QtCore import (Signal, QMetaObject, Slot)

from view.BaseWidgets import BaseFrame


class FramesWidget(BaseFrame):
    rejected = Signal()
    accepted = Signal()
    back = Signal()

    def __init__(self, parent=None):
        super(FramesWidget, self).__init__(parent)
        self.config_frames = []
        self.frames_instances = []
        self.current_frame = 0

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.frames_widget = QWidget(self)
        self.frames_widget.setContentsMargins(0, 0, 0, 0)
        self.frames_widget_layout = QGridLayout(self.frames_widget)
        self.frames_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.addWidget(self.frames_widget)

        self.btn_box = QDialogButtonBox(self)
        self.btn_box.setObjectName("btn_box")
        self.btn_box.setStandardButtons(QDialogButtonBox.Reset | QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.btn_box.button(QDialogButtonBox.Reset).setText("Back")
        self.btn_box.button(QDialogButtonBox.Ok).setText("Next")
        self.widget_layout.addWidget(self.btn_box)

        self.btn_box.button(QDialogButtonBox.Reset).clicked.connect(self.on_btn_box_resetted)
        QMetaObject.connectSlotsByName(self)

    def add_frames(self, frames):
        for frame in frames:
            self.add_frame(frame)

    def add_frame(self, frame):
        f = frame(self.frames_widget)
        f.setVisible(False)
        f.set_next_enabled.connect(self.btn_box.button(QDialogButtonBox.Ok).setEnabled)
        self.frames_widget_layout.addWidget(f, 0, 0, 1, 1)
        self.frames_instances.append(f)

        if len(self.frames_instances) > 0:
            self.frames_instances[0].setVisible(True)
            if self.frames_instances[0].disable_next_on_enter:
                self.btn_box.button(QDialogButtonBox.Ok).setEnabled(False)

    @Slot()
    def collect_info(self) -> dict:
        """Get info from every page"""
        settings = {}
        for frame in self.frames_instances:
            settings = settings | frame.collect_info()
        return settings

    @Slot()
    def on_btn_box_rejected(self):
        """When user clicks cancel button"""
        self.rejected.emit()

    @Slot()
    def on_btn_box_accepted(self):
        """On Next button clicked"""
        if self.current_frame + 1 < len(self.frames_instances):
            # if not last
            self.frames_instances[self.current_frame].setVisible(False)
            self.current_frame = self.current_frame + 1
            self.frames_instances[self.current_frame].setVisible(True)

            # if disable on enter page
            self.btn_box.button(QDialogButtonBox.Ok).setEnabled(
                not self.frames_instances[self.current_frame].disable_next_on_enter)

            # if next page is last
            self._change_next_finish()

        # if last page
        elif self.current_frame + 1 == len(self.frames_instances):
            self.accepted.emit()

    @Slot()
    def on_btn_box_resetted(self):
        """On Back button clicked."""
        if self.current_frame > 0:
            self.frames_instances[self.current_frame].setVisible(False)
            self.current_frame = self.current_frame - 1
            self.frames_instances[self.current_frame].setVisible(True)
            self._change_next_finish()

            self.btn_box.button(QDialogButtonBox.Ok).setEnabled(
                not self.frames_instances[self.current_frame].disable_next_on_enter)
        else:
            self.back.emit()

    def _change_next_finish(self):
        if self.current_frame + 1 == len(self.frames_instances):
            self.btn_box.button(QDialogButtonBox.Ok).setText("Finish")
        else:
            self.btn_box.button(QDialogButtonBox.Ok).setText("Next")
