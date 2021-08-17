from qtpy.QtWidgets import QTabWidget
from qtpy.QtCore import Signal, Slot
from qrainbowstyle.windows import FramelessWindow

from models.Bot import Bot
from models.Events import Task

from .Widgets import TasksWidget, AttributesWidget, ShellWidget, ModulesWidget, RelayWidget, LogsWidget


class DeviceWindow(FramelessWindow):
    stop_task = Signal(Bot, Task)
    force_start_task = Signal(Bot, Task)
    run_shell = Signal(Bot, str)

    def __init__(self, bot, parent):
        super(DeviceWindow, self).__init__(parent)
        self.setContentsMargins(11, 11, 11, 11)

        self.tab_widget = QTabWidget(self)
        self.addContentWidget(self.tab_widget)

        self.tasks_tab = TasksWidget(bot, self)
        self.tasks_tab.stop_task.connect(self.stop_task.emit)
        self.tasks_tab.force_start_task.connect(self.force_start_task.emit)

        self.shell_tab = ShellWidget(bot, self)
        self.shell_tab.run_shell.connect(self.run_shell.emit)

        self.modules_tab = ModulesWidget(bot, self)

        self.relay_tab = RelayWidget(bot, self)

        self.logs_tab = LogsWidget(bot, self)

        self.attributes_tab = AttributesWidget(bot, self)
        self.attributes_tab.update_attributes(bot)

        self.tab_widget.addTab(self.tasks_tab, "Tasks")
        self.tab_widget.addTab(self.modules_tab, "Modules")
        self.tab_widget.addTab(self.shell_tab, "Shell")
        self.tab_widget.addTab(self.relay_tab, "Relay")
        self.tab_widget.addTab(self.logs_tab, "Log")
        self.tab_widget.addTab(self.attributes_tab, "Information")

    @Slot(list)
    def update_attributes(self, info):
        if self.isVisible():
            self.attributes_tab.update_attributes(info)

    @Slot(list)
    def update_tasks(self, tasks):
        if self.isVisible():
            self.tasks_tab.update_tasks(tasks)

    @Slot(Bot, str)
    def append_shell(self, device, output):
        if self.isVisible():
            self.shell_tab.append_shell(device, output)

    @Slot()
    def close(self):
        super().close()
        self.deleteLater()
