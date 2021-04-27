from qtpy.QtWidgets import QWidget, QFormLayout, QMenu, QAction, QLabel, QHBoxLayout
from qtpy.QtCore import Signal, Slot
from qtpy.QtGui import QCursor, QCloseEvent

from models import Task
from models.EventsTable import TasksTableModel

from view.BaseWidgets.QTable import TasksTable
from view.DeviceWindow.TaskWindow import TaskWindow


class WidgetWithCloseSignal(QWidget):
    """WidgetWithCloseSignal documentation"""
    closed = Signal()

    def __init__(self, parent):
        super(WidgetWithCloseSignal, self).__init__(parent)

    @Slot(QCloseEvent)
    def closeEvent(self, event) -> None:
        self.closed.emit()
        return super().closeEvent(event)

    @Slot(Signal)
    def disconnectSignal(self, sig):
        try:
            sig.disconnect()
        except Exception:  # noqa
            pass


class DeviceInfoWidget(WidgetWithCloseSignal):
    """Shows info about device."""

    def __init__(self, parent):
        super(DeviceInfoWidget, self).__init__(parent)
        self.tab_name = "Info"

        self.widget_layout = QHBoxLayout(self)
        self.setLayout(self.widget_layout)

        # widget with ifno - ip, id, location...
        self.info_widget = QWidget(self)
        self.info_widget_layout = QFormLayout(self.info_widget)
        self.info_widget.setLayout(self.info_widget_layout)
        self.widget_layout.addWidget(self.info_widget)

        # widget with actions - remote shell, powershell, remote screen...
        self.actions_widget = QWidget(self)
        self.actions_widget_layout = QFormLayout(self.actions_widget)
        self.actions_widget.setLayout(self.actions_widget_layout)

    def updateInfo(self, bot):
        # update labels with info about bot - ip, location...

        self.device_id_label = QLabel(self.info_widget)
        self.device_id_label.setText("Device ID")

        self.device_id_value = QLabel(self.info_widget)
        self.device_id_value.setText(str(bot.id))

        self.creation_time_label = QLabel(self.info_widget)
        self.creation_time_label.setText("Creation time")

        self.creation_time_value = QLabel(self.info_widget)
        self.creation_time_value.setText(str(bot.creation_time))

        self.ip_label = QLabel(self.info_widget)
        self.ip_label.setText("IP address")

        self.ip_value = QLabel(self.info_widget)
        self.ip_value.setText(str(bot.ip))

        self.public_ip_label = QLabel(self.info_widget)
        self.public_ip_label.setText("Public IP")

        self.public_ip_value = QLabel(self.info_widget)
        self.public_ip_value.setText(str(bot.public_ip))

        self.location_label = QLabel(self.info_widget)
        self.location_label.setText("Location")

        self.location_value = QLabel(self.info_widget)
        self.location_value.setText("{}, {}".format(bot.geolocation[0], bot.geolocation[1]))

        self.platform_label = QLabel(self.info_widget)
        self.platform_label.setText("Platform")

        self.platform_value = QLabel(self.info_widget)
        self.platform_value.setText(str(bot.platform))

        self.architecture_label = QLabel(self.info_widget)
        self.architecture_label.setText("Architecture")

        self.architecture_value = QLabel(self.info_widget)
        self.architecture_value.setText(str(bot.architecture))

        self.system_architecture_label = QLabel(self.info_widget)
        self.system_architecture_label.setText("System architecture")

        self.system_architecture_value = QLabel(self.info_widget)
        self.system_architecture_value.setText(str(bot.system_architecture))

        self.username_label = QLabel(self.info_widget)
        self.username_label.setText("Username")

        self.username_value = QLabel(self.info_widget)
        self.username_value.setText(str(bot.username))

        self.administrator_label = QLabel(self.info_widget)
        self.administrator_label.setText("Administrator")

        self.administrator_value = QLabel(self.info_widget)
        self.administrator_value.setText(str(bot.administrator))

        self.language_label = QLabel(self.info_widget)
        self.language_label.setText("Language")

        self.language_value = QLabel(self.info_widget)
        self.language_value.setText(str(bot.language))

        self.tasks_count_label = QLabel(self.info_widget)
        self.tasks_count_label.setText("Tasks")

        self.tasks_count_value = QLabel(self.info_widget)
        self.tasks_count_value.setText(str(len(bot.tasks)))

        self.info_widget_layout.addRow(self.device_id_label, self.device_id_value)
        self.info_widget_layout.addRow(self.creation_time_label, self.creation_time_value)
        self.info_widget_layout.addRow(self.ip_label, self.ip_value)
        self.info_widget_layout.addRow(self.public_ip_label, self.public_ip_value)
        self.info_widget_layout.addRow(self.location_label, self.location_value)
        self.info_widget_layout.addRow(self.platform_label, self.platform_value)
        self.info_widget_layout.addRow(self.architecture_label, self.architecture_value)
        self.info_widget_layout.addRow(self.system_architecture_label, self.system_architecture_value)
        self.info_widget_layout.addRow(self.username_label, self.username_value)
        self.info_widget_layout.addRow(self.administrator_label, self.administrator_value)
        self.info_widget_layout.addRow(self.language_label, self.language_value)
        self.info_widget_layout.addRow(self.tasks_count_label, self.tasks_count_value)


class DeviceTasksWidget(WidgetWithCloseSignal):
    """Shows tasks table."""
    stop_task = Signal(int, int)

    def __init__(self, bot, parent):
        super(DeviceTasksWidget, self).__init__(parent)
        self.tab_name = "Tasks"
        self.bot_id = bot.get_id()

        self.widget_layout = QHBoxLayout(self)
        self.setLayout(self.widget_layout)
        self.table = TasksTable(self)
        self.table.context_menu_requested.connect(self.showContextMenu)
        self.table.task_double_clicked.connect(self.showTaskWindow)
        self.widget_layout.addWidget(self.table)

        self.model = TasksTableModel(self)
        self.model.setEvents(bot.tasks)
        bot.updated.connect(lambda: self.model.setEvents(bot.tasks))
        self.closed.connect(lambda: self.disconnectSignal(bot.updated))
        self.table.setModel(self.model)

    def updateTasks(self, data):
        self.model.setEvents(data)

    @Slot(Task)
    def showTaskWindow(self, task: Task):
        self.task_window = TaskWindow(self)
        self.task_window.setTask(task)
        self.task_window.show()

    @Slot(int)
    def showContextMenu(self, task_id) -> None:
        self.menu = QMenu(self)
        stop_action = QAction('Stop', self)
        stop_action.triggered.connect(lambda: self.stop_task.emit(self.bot_id, task_id))
        self.menu.addAction(stop_action)
        self.menu.popup(QCursor.pos())
