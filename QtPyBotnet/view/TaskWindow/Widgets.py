from qtpy.QtCore import Signal, Slot
from qtpy.QtWidgets import (QWidget, QHBoxLayout, QGroupBox, QCheckBox, QLineEdit, QDateTimeEdit,
                            QTextEdit, QSpinBox, QVBoxLayout, QRadioButton, QFormLayout, QLabel)

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
        self.radios = []

        self.tasks = ConfigManager().get_tasks()
        for task in self.tasks:
            radio = QRadioButton(task.__name__, self)
            radio.clicked.connect(lambda _, t=task: self.selection_changed.emit(t))
            radio.setToolTip(task.description)
            self.widget_layout.addWidget(radio)
            self.radios.append(radio)

    @Slot()
    def on_send_button_clicked(self):
        for radio in self.radios:
            if radio.isChecked():
                self.send_task.emit(int(self.bot_edit.value()), str(radio.text()))
                return


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
            key_label = QLabel(str(key), self)
            val_type = value.get("type")
            default = value.get("default")

            if val_type is int:
                widget = QSpinBox(self)
                widget.setRange(0, 100000)
                widget.setValue(int(default))
            elif val_type is str:
                widget = QLineEdit(self)
                widget.setText(str(default))
            elif val_type is bool:
                key_label = None
                widget = QCheckBox(str(key), self)
                widget.setChecked(bool(default))
            elif val_type == "text":
                widget = QTextEdit(self)
                widget.setText(str(default))
            else:
                continue

            widget.setObjectName(key)
            widget.setToolTip(value.get("description"))
            self.widgets.append({"key": key_label, "value": widget})
            self.widget_layout.addRow(key_label, widget)

    def get_kwargs(self):
        kwargs = {}
        for widget in self.widgets:
            if type(widget) == QSpinBox:
                kwargs[widget.objectName()] = widget.value()
            elif type(widget) == QLineEdit:
                kwargs[widget.objectName()] = widget.text()
            elif type(widget) == QTextEdit:
                kwargs[widget.objectName()] = widget.toPlainText()
            elif type(widget) == QCheckBox:
                kwargs[widget.objectName()] = widget.isChecked()
        return kwargs
