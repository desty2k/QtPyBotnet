from qtpy.QtCore import Signal, Slot
from qtpy.QtWidgets import QWidget, QHBoxLayout, QGroupBox, QCheckBox, QLineEdit, QTextEdit, QSpinBox, QVBoxLayout, QRadioButton

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

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.setTitle("Options")

    @Slot(type)
    def set_kwargs(self, task):
        if task is self.current_task:
            return

        if task is not self.current_task:
            for widget in self.widgets:
                widget.setParent(None)
                widget.deleteLater()
                self.widget_layout.removeWidget(widget)
            self.widgets.clear()
            self.current_task = task

        if not task:
            return

        kwargs_dict = task.kwargs
        for key, value in kwargs_dict.items():
            val_type = value.get("type")
            if val_type == "int":
                widget = QSpinBox(self)
            elif val_type == "str":
                widget = QLineEdit(self)
            elif val_type == "text":
                widget = QTextEdit(self)
            elif val_type == "bool":
                widget = QCheckBox(str(key), self)
            else:
                return

            widget.setObjectName(key)
            widget.setToolTip(value.get("description"))
            self.widgets.append(widget)
            self.widget_layout.addWidget(widget)

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
