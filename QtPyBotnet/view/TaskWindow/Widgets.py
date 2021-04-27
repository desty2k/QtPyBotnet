from qtpy.QtCore import Signal, Slot, Qt, QDateTime
from qtpy.QtWidgets import (QWidget, QHBoxLayout, QGroupBox, QCheckBox, QLineEdit, QComboBox, QListWidget, QPushButton,
                            QTextEdit, QSpinBox, QVBoxLayout, QRadioButton, QFormLayout, QLabel, QDateTimeEdit)

from core.config import ConfigManager
from models import Task


class MainTaskWidget(QWidget):
    send_task = Signal(int, str, dict, int)

    def __init__(self, parent):
        super(MainTaskWidget, self).__init__(parent)

        self.widget_layout = QHBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.selection_widget = TaskSelectionGroupBox(self)
        self.widget_layout.addWidget(self.selection_widget)

        self.kwargs_widget = TaskKwargsGroupBox(self)
        self.widget_layout.addWidget(self.kwargs_widget)

        self.time_widget = TaskOptionsGroupBox(self)
        self.widget_layout.addWidget(self.time_widget)

        self.send_button = QPushButton(self)
        self.send_button.setText("Send")
        self.widget_layout.addWidget(self.send_button)

        self.send_button.clicked.connect(self.on_send_button_clicked)
        self.selection_widget.selection_changed.connect(self.kwargs_widget.set_kwargs)

    @Slot()
    def on_send_button_clicked(self):
        self.send_task.emit(0, self.selection_widget.get_task(),
                            self.kwargs_widget.get_kwargs(), int(self.time_widget.get_options().get("user_activity")))


class TaskOptionsGroupBox(QGroupBox):

    def __init__(self, parent):
        super(TaskOptionsGroupBox, self).__init__(parent)
        self.widget_layout = QFormLayout(self)
        self.setLayout(self.widget_layout)
        self.setTitle("Time")

        self.time_label = QLabel(self)
        self.time_label.setText("Execute: ")

        self.time_now = QRadioButton(self)
        self.time_now.setText("Immediately")
        self.time_now.setChecked(True)

        self.time_schedule = QRadioButton(self)
        self.time_schedule.setText("Schedule")

        self.schedule_select = QDateTimeEdit(self)
        self.schedule_select.setDateTime(QDateTime.currentDateTime())
        self.schedule_select.setEnabled(False)

        self.user_activity_label = QLabel(self)
        self.user_activity_label.setText("User activity")

        self.user_activity_combo = QComboBox(self)
        self.user_activity_combo.addItems(["0 - Disabled", "1 - Low", "2 - Normal",
                                           "3 - Medium", "4 - High", "5 - Very high"])

        self.widget_layout.addRow(self.time_label, None)
        self.widget_layout.addRow(self.time_now, None)
        self.widget_layout.addRow(self.time_schedule, self.schedule_select)
        self.widget_layout.addRow(self.user_activity_label, self.user_activity_combo)

        self.time_schedule.toggled.connect(self.on_time_schedule_toggled)

    @Slot(bool)
    def on_time_schedule_toggled(self, state):
        if state:
            self.schedule_select.setEnabled(True)
        else:
            self.schedule_select.setEnabled(False)

    def get_options(self):
        resp = {"user_activity": self.user_activity_combo.currentText().split(" - ")[0]}

        if self.time_now.isChecked():
            resp["time"] = "now"

        elif self.time_schedule.isChecked():
            resp["time"] = self.schedule_select.dateTime().toString()
        return resp


class TaskSelectionGroupBox(QGroupBox):
    selection_changed = Signal(type)

    def __init__(self, parent):
        super(TaskSelectionGroupBox, self).__init__(parent)
        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)
        self.setTitle("Tasks")

        self.combo = QComboBox(self)
        self.combo.currentTextChanged.connect(lambda text: self.selection_changed.emit(self.get_task_by_name(text)))
        self.widget_layout.addWidget(self.combo)

        self.tasks = ConfigManager().get_tasks()
        for index, task in enumerate(self.tasks):
            if not task.experimental:
                self.combo.addItem(task.__name__)
                self.combo.setItemData(index, task.description, Qt.ToolTipRole)

    def get_task_by_name(self, name):
        for task in self.tasks:
            if task.__name__ == name:
                return task

    def get_task(self):
        return self.combo.currentText()


class TaskKwargsGroupBox(QGroupBox):

    def __init__(self, parent):
        super(TaskKwargsGroupBox, self).__init__(parent)
        self.widgets = []
        self.current_task = None

        self.widget_layout = QFormLayout(self)
        self.setLayout(self.widget_layout)

        self.setTitle("Options")

    @Slot(type)
    def set_kwargs(self, task):
        """Creates widgets for each task keyword argument."""
        if not task or task is self.current_task:
            return
        else:
            for widget_dict in self.widgets:
                key_widget = widget_dict.get("key")
                value_widget = widget_dict.get("value")

                if key_widget:
                    key_widget.setParent(None)
                    self.widget_layout.removeWidget(key_widget)

                value_widget.setParent(None)
                self.widget_layout.removeWidget(value_widget)
            self.widgets.clear()
            self.current_task = task

        kwargs_dict = task.kwargs
        for key, value in kwargs_dict.items():
            key_label = QLabel(str(key).replace("_", " ").capitalize(), self)
            val_type = value.get("type")
            default = value.get("default")

            if val_type is int:
                value_widget = QSpinBox(self)
                value_widget.setRange(-1, 100000)
                value_widget.setValue(int(default))
            elif val_type is list:
                value_widget = QListWidget(self)
                value_widget.addItems([str(item) for item in default])
                for i in range(value_widget.count()):
                    value_widget.item(i).setFlags(value_widget.item(i).flags() | Qt.ItemIsEditable)
            elif val_type is str:
                value_widget = QLineEdit(self)
                value_widget.setText(str(default))
            elif val_type is bool:
                key_label = None
                value_widget = QCheckBox(str(key).replace("_", " ").capitalize(), self)
                value_widget.setChecked(bool(default))
            elif val_type == "text":
                value_widget = QTextEdit(self)
                value_widget.setText(str(default))
            else:
                continue

            value_widget.setObjectName(key)
            value_widget.setToolTip(value.get("description"))
            self.widgets.append({"key": key_label, "value": value_widget})
            self.widget_layout.addRow(key_label, value_widget)

    def get_kwargs(self):
        """Returns user arguments"""
        kwargs = {}
        for widget_dict in self.widgets:
            value_widget = widget_dict.get("value")
            if type(value_widget) == QSpinBox:
                kwargs[value_widget.objectName()] = value_widget.value()
            elif type(value_widget) == QListWidget:
                kwargs[value_widget.objectName()] = [value_widget.item(x).text() for x in range(value_widget.count())]
            elif type(value_widget) == QLineEdit:
                kwargs[value_widget.objectName()] = value_widget.text()
            elif type(value_widget) == QTextEdit:
                kwargs[value_widget.objectName()] = value_widget.toPlainText()
            elif type(value_widget) == QCheckBox:
                kwargs[value_widget.objectName()] = value_widget.isChecked()
        return kwargs
