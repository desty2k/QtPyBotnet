from qtpy.QtWidgets import (QDialogButtonBox, QVBoxLayout, QWidget, QFrame, QRadioButton, QPushButton, QGroupBox,
                            QFormLayout, QLabel, QSpinBox, QCheckBox, QDateEdit)
from qtpy.QtCore import (Signal, QMetaObject, Slot, Qt, QDateTime)

from qrainbowstyle.windows import FramelessWindow

from QtPyBotnet.core.config import ConfigManager
from view.TaskWindow.Widgets import MainTaskWidget


class TaskWindow(FramelessWindow):
    send_task = Signal(int, str)

    def __init__(self, parent):
        super(TaskWindow, self).__init__(parent)
        self.radios = []

        self.content_widget = MainTaskWidget(self)
        self.addContentWidget(self.content_widget)


# class TaskWindow(FramelessWindow):
#     send_task = Signal(int, str)
#
#     def __init__(self, parent):
#         super(TaskWindow, self).__init__(parent)
#         self.setObjectName("task_window")
#         self.radios = []
#         self.tasks = ConfigManager().get_tasks()
#
#         self.task_widget = QWidget(self)
#         self.task_layout = QVBoxLayout(self.task_widget)
#         self.task_widget.setLayout(self.task_layout)
#         self.addContentWidget(self.task_widget)
#
#         self.radio_group = QGroupBox(self.task_widget)
#         self.radio_group.setTitle("Tasks")
#         self.radio_layout = QVBoxLayout(self.radio_group)
#         self.radio_group.setLayout(self.radio_layout)
#
#         for task in self.tasks:
#             radio = QRadioButton(task.__name__, self.radio_group)
#             radio.setToolTip(task.description)
#             self.radio_layout.addWidget(radio)
#             self.radios.append(radio)
#
#         self.options_group = QGroupBox(self.task_widget)
#         self.options_group.setTitle("Options")
#         self.options_layout = QFormLayout(self.options_group)
#         self.options_group.setLayout(self.options_layout)
#
#         # bot
#         self.bot_label = QLabel(self.options_group)
#         self.bot_label.setObjectName("bot_label")
#         self.bot_label.setText("Bot ID")
#         self.options_layout.setWidget(0, QFormLayout.LabelRole, self.bot_label)
#
#         self.bot_edit = QSpinBox(self.options_group)
#         self.bot_edit.setObjectName("bot_edit")
#         self.bot_edit.setValue(0)
#         self.bot_edit.setToolTip("Enter 0 to send to all bots")
#         self.options_layout.setWidget(0, QFormLayout.FieldRole, self.bot_edit)
#
#         # activity
#         self.activity_label = QLabel(self.options_group)
#         self.activity_label.setObjectName("activity_label")
#         self.activity_label.setText("User activity")
#         self.options_layout.setWidget(1, QFormLayout.LabelRole, self.activity_label)
#
#         self.activity_edit = QSpinBox(self.options_group)
#         self.activity_edit.setObjectName("activity_edit")
#         self.activity_edit.setValue(0)
#         self.activity_edit.setRange(0, 5)
#         self.activity_edit.setToolTip("Enter 0 to disable")
#         self.options_layout.setWidget(1, QFormLayout.FieldRole, self.activity_edit)
#
#         # schedule date
#         self.schedule_label = QCheckBox(self.options_group)
#         self.schedule_label.setObjectName("schedule_label")
#         self.schedule_label.setText("Schedule")
#         self.options_layout.setWidget(2, QFormLayout.LabelRole, self.schedule_label)
#
#         self.schedule_edit = QDateEdit(self.options_group, calendarPopup=True)
#         self.schedule_edit.setDateTime(QDateTime.currentDateTime())
#         self.schedule_edit.setObjectName("schedule_edit")
#         self.schedule_edit.setEnabled(False)
#         self.options_layout.setWidget(2, QFormLayout.FieldRole, self.schedule_edit)
#         self.schedule_label.stateChanged.connect(self.schedule_edit.setEnabled)
#
#         # send button
#         self.send_button = QPushButton(self.task_widget)
#         self.send_button.setMinimumHeight(35)
#         self.send_button.setObjectName("send_button")
#         self.send_button.setText("Send task")
#
#         self.task_layout.addWidget(self.radio_group)
#         self.task_layout.addWidget(self.options_group)
#         self.task_layout.addWidget(self.send_button)
#         QMetaObject.connectSlotsByName(self)
#
#     def setupUi(self):
#         pass
#
#     @Slot()
#     def on_send_button_clicked(self):
#         for radio in self.radios:
#             if radio.isChecked():
#                 self.send_task.emit(int(self.bot_edit.value()), str(radio.text()))
#                 return
