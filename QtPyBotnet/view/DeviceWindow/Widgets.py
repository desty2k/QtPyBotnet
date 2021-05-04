from qtpy.QtWidgets import QWidget, QFormLayout, QMenu, QAction, QLabel, QHBoxLayout
from qtpy.QtCore import Signal, Slot
from qtpy.QtGui import QCursor, QCloseEvent

from models import Task, Bot
from models.EventsTable import TasksTableModel

from view.BaseWidgets.BotnetTableView import TasksTableView
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
        self.widgets = []

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

    @Slot(Bot)
    def updateInfo(self, bot):
        # update labels with info about bot - ip, location...
        self.widgets.clear()
        for var, val in vars(bot).items():
            label = QLabel(self.info_widget)
            label.setText(" ".join(var.split("_")).capitalize())

            field = QLabel(self.info_widget)
            field.setText(str(val))
            self.widgets.append({"label": label, "field": field})
            self.info_widget_layout.addRow(label, field)


class DeviceTasksWidget(WidgetWithCloseSignal):
    """Shows tasks table."""
    stop_task = Signal(int, int)

    def __init__(self, bot, parent):
        super(DeviceTasksWidget, self).__init__(parent)
        self.tab_name = "Tasks"
        self.bot_id = bot.get_id()

        self.widget_layout = QHBoxLayout(self)
        self.setLayout(self.widget_layout)
        self.table = TasksTableView(self)
        self.table.context_menu_requested.connect(self.showContextMenu)
        self.table.task_double_clicked.connect(self.showTaskWindow)
        self.widget_layout.addWidget(self.table)

        self.model = TasksTableModel(self)
        self.model.setBot(bot)
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
