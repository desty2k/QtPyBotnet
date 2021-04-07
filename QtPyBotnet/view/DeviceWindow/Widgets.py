from qtpy.QtWidgets import QWidget, QVBoxLayout, QMenu, QAction, QLabel, QHBoxLayout
from qtpy.QtCore import Signal, Slot
from qtpy.QtGui import QCursor, QCloseEvent

from QtPyBotnet.view.BaseWidgets.QTable import TasksTable, ModulesTable
from QtPyBotnet.models.EventsTable import TasksTableModel, ModulesTableModel

from QtPyBotnet.models import Task
from view.DeviceWindow import TaskWindow


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

        self.widget_layout = QVBoxLayout(self)
        self.setLayout(self.widget_layout)

    def updateInfo(self, bot):
        # update labels with info about bot - ip, location...
        self.ip_label = QLabel(self)
        self.ip_label.setText(bot.ip)
        self.widget_layout.addWidget(self.ip_label)

        self.public_ip_label = QLabel(self)
        self.public_ip_label.setText(bot.public_ip)
        self.widget_layout.addWidget(self.public_ip_label)

        self.location_label = QLabel(self)
        self.location_label.setText("{}, {}".format(bot.geolocation[0], bot.geolocation[1]))
        self.widget_layout.addWidget(self.location_label)


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


class DeviceModulesWidget(WidgetWithCloseSignal):
    """Shows modules and its states."""
    toggle_module = Signal(int, str, bool)

    def __init__(self, bot, parent):
        super(DeviceModulesWidget, self).__init__(parent)
        self.tab_name = "Modules"
        self.bot_id = bot.get_id()

        self.widget_layout = QHBoxLayout(self)
        self.setLayout(self.widget_layout)
        self.table = ModulesTable(self)
        self.table.context_menu_requested.connect(self.showContextMenu)
        self.widget_layout.addWidget(self.table)

        self.model = ModulesTableModel(self)
        self.model.setEvents(bot.modules)
        bot.updated.connect(lambda: self.model.setEvents(bot.modules))
        self.closed.connect(lambda: self.disconnectSignal(bot.updated))
        self.table.setModel(self.model)

    def updateModules(self, data):
        self.model.setEvents(data)

    @Slot(str)
    def showContextMenu(self, module_name) -> None:
        self.menu = QMenu(self)
        enable_action = QAction('Enable', self)
        enable_action.triggered.connect(
            lambda: self.toggle_module.emit(self.bot_id, module_name, True))
        self.menu.addAction(enable_action)

        disable_action = QAction('Disable', self)
        disable_action.triggered.connect(
            lambda: self.toggle_module.emit(self.bot_id, module_name, False))
        self.menu.addAction(disable_action)
        self.menu.popup(QCursor.pos())
