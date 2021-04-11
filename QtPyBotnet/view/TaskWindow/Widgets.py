from qtpy.QtCore import Signal, Slot, Qt
from qtpy.QtWidgets import (QWidget, QHBoxLayout, QGroupBox, QCheckBox, QLineEdit, QComboBox,
                            QTextEdit, QSpinBox, QVBoxLayout, QRadioButton, QFormLayout, QLabel, QDateTimeEdit)

from core.config import ConfigManager


class MainTaskWidget(QWidget):
    """MainTaskWidget documentation"""

    def __init__(self, parent):
        super(MainTaskWidget, self).__init__(parent)

        self.widget_layout = QHBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.selection_widget = SelectionWidget(self)
        self.widget_layout.addWidget(self.selection_widget)

        self.kwargs_widget = KwargsWidget(self)
        self.widget_layout.addWidget(self.kwargs_widget)
        self.selection_widget.selection_changed.connect(self.kwargs_widget.set_kwargs)


class SelectionWidget(QGroupBox):
    selection_changed = Signal(type)

    def __init__(self, parent):
        super(SelectionWidget, self).__init__(parent)
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

    @Slot()
    def on_send_button_clicked(self):
        self.send_task.emit(int(self.bot_edit.value()), str(self.combo.currentText()))


class KwargsWidget(QGroupBox):

    def __init__(self, parent):
        super(KwargsWidget, self).__init__(parent)
        self.widgets = []
        self.current_task = None

        self.widget_layout = QFormLayout(self)
        self.setLayout(self.widget_layout)

        self.setTitle("Options")

    @Slot(type)
    def set_kwargs(self, task):
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
        kwargs = {}
        for widget_dict in self.widgets:
            value_widget = widget_dict.get("value")
            if type(value_widget) == QSpinBox:
                kwargs[value_widget.objectName()] = value_widget.value()
            elif type(value_widget) == QLineEdit:
                kwargs[value_widget.objectName()] = value_widget.text()
            elif type(value_widget) == QTextEdit:
                kwargs[value_widget.objectName()] = value_widget.toPlainText()
            elif type(value_widget) == QCheckBox:
                kwargs[value_widget.objectName()] = value_widget.isChecked()
        return kwargs
