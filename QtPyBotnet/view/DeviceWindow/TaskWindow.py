from qtpy.QtWidgets import QWidget, QFormLayout, QLabel, QScrollArea, QHBoxLayout, QListView, QLineEdit, QTextEdit
from qtpy.QtGui import QPixmap, QStandardItem, QStandardItemModel
from qtpy.QtCore import Qt

from base64 import b64decode

from qrainbowstyle.windows import FramelessWindow

from models import Task


class StringDictWidget(QWidget):

    def __init__(self, parent):
        super(StringDictWidget, self).__init__(parent)
        self.setContentsMargins(11, 11, 11, 11)
        self.widget_layout = QFormLayout(self)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.widget_layout)

    def addEntry(self, key, value):
        key_label = QLabel(self)
        key_label.setText(str(key))

        value_label = QLabel(self)
        value_label.setText(str(value))
        self.widget_layout.addRow(key_label, value_label)


class PixmapGallery(QScrollArea):

    def __init__(self, parent):
        super(PixmapGallery, self).__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.labels = []
        self.widget_layout = QHBoxLayout(self)
        self.setLayout(self.widget_layout)

    def addFromBase64(self, data):
        data = b64decode(data)
        label = QLabel(self)
        label.setScaledContents(True)
        self.labels.append(label)
        self.widget_layout.addWidget(label)

        pix = QPixmap()
        pix.loadFromData(data, "PNG")
        pix.scaled(label.width(), label.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        label.setPixmap(pix)


class StringListWidget(QListView):

    def __init__(self, parent):
        super(StringListWidget, self).__init__(parent)
        self.model = QStandardItemModel(self)
        self.setModel(self.model)

    def setData(self, data: list):
        for entry in data:
            item = QStandardItem(str(entry))
            self.model.appendRow(item)

    def addData(self, data: str):
        item = QStandardItem(str(data))
        self.model.appendRow(item)


class TaskWindow(FramelessWindow):

    def __init__(self, parent):
        super(TaskWindow, self).__init__(parent)
        self.content_widget = QWidget(self)
        self.widget_layout = QFormLayout(self.content_widget)
        self.content_widget.setLayout(self.widget_layout)
        self.addContentWidget(self.content_widget)

        self.task_id_label = QLabel(self.content_widget)
        self.task_id_label.setObjectName("task_id_label")
        self.task_id_label.setText("Task ID")
        self.widget_layout.setWidget(0, QFormLayout.LabelRole, self.task_id_label)

        self.task_id_value = QLabel(self.content_widget)
        self.task_id_value.setObjectName("task_id_value")
        self.widget_layout.setWidget(0, QFormLayout.FieldRole, self.task_id_value)

        self.task_label = QLabel(self.content_widget)
        self.task_label.setObjectName("task_label")
        self.task_label.setText("Task")
        self.widget_layout.setWidget(1, QFormLayout.LabelRole, self.task_label)

        self.task_value = QLabel(self.content_widget)
        self.task_value.setObjectName("task_value")
        self.widget_layout.setWidget(1, QFormLayout.FieldRole, self.task_value)

        self.task_time_label = QLabel(self.content_widget)
        self.task_time_label.setObjectName("task_time_label")
        self.task_time_label.setText("Time")
        self.widget_layout.setWidget(2, QFormLayout.LabelRole, self.task_time_label)

        self.task_time_value = QLabel(self.content_widget)
        self.task_time_value.setObjectName("task_time_value")
        self.widget_layout.setWidget(2, QFormLayout.FieldRole, self.task_time_value)

        self.user_activity_label = QLabel(self.content_widget)
        self.user_activity_label.setObjectName("user_activity_label")
        self.user_activity_label.setText("User activity")
        self.widget_layout.setWidget(3, QFormLayout.LabelRole, self.user_activity_label)

        self.user_activity_value = QLabel(self.content_widget)
        self.user_activity_value.setObjectName("user_activity_value")
        self.widget_layout.setWidget(3, QFormLayout.FieldRole, self.user_activity_value)

        self.state_label = QLabel(self.content_widget)
        self.state_label.setObjectName("state_label")
        self.state_label.setText("State")
        self.widget_layout.setWidget(4, QFormLayout.LabelRole, self.state_label)

        self.state_value = QLabel(self.content_widget)
        self.state_value.setObjectName("state_value")
        self.widget_layout.setWidget(4, QFormLayout.FieldRole, self.state_value)

        self.result_label = QLabel(self.content_widget)
        self.result_label.setObjectName("state_label")
        self.result_label.setText("Result")
        self.widget_layout.setWidget(6, QFormLayout.LabelRole, self.result_label)

        self.exit_code_label = QLabel(self.content_widget)
        self.exit_code_label.setObjectName("exit_code_label")
        self.exit_code_label.setText("Exit code")
        self.widget_layout.setWidget(5, QFormLayout.LabelRole, self.exit_code_label)

        self.exit_code_value = QLabel(self.content_widget)
        self.exit_code_value.setObjectName("exit_code_value")
        self.widget_layout.setWidget(5, QFormLayout.FieldRole, self.exit_code_value)

    def setTask(self, task: Task):
        self.task_id_value.setText(str(task.id))
        self.task_value.setText(str(task.task))
        self.task_time_value.setText(str(task.time_created))
        self.user_activity_value.setText(str(task.user_activity))
        self.state_value.setText(str(task.user_activity))
        self.exit_code_value.setText(str(task.exit_code))

        result_type = type(task.result)
        if result_type is dict:
            if task.result.get("type") == "images":
                self.state_value = PixmapGallery(self)
                for img in task.result.get("images"):
                    self.state_value.addFromBase64(img)
            else:
                self.state_value = StringDictWidget(self)
                for item, key in task.result.items():
                    self.state_value.addEntry(item, key)

        elif result_type is list:
            self.state_value = StringListWidget(self)
            self.state_value.setData(task.result)

        elif result_type is str:
            if len(task.result) <= 100:
                self.state_value = QLineEdit(self.content_widget)
                self.state_value.setText(str(task.result))
            else:
                self.state_value = QTextEdit(self.content_widget)
                self.state_value.setText(str(task.result))
        else:
            self.state_value = QLabel(self.content_widget)
            self.state_value.setText(str(task.result))

        self.state_value.setObjectName("state_value")
        self.widget_layout.setWidget(6, QFormLayout.FieldRole, self.state_value)
