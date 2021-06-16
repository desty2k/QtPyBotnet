from qtpy.QtWidgets import QTabWidget
from qtpy.QtCore import Signal, Slot
from qrainbowstyle.windows import FramelessWindow
from .Widgets import DeviceInfoWidget, DeviceTasksWidget, ShellWidget


class DeviceWindow(FramelessWindow):
    stop_task = Signal(int, int)
    force_start_task = Signal(int, int)
    run_shell = Signal(int, str)

    def __init__(self, bot, parent):
        super(DeviceWindow, self).__init__(parent)
        self.setContentsMargins(11, 11, 11, 11)

        self.tab_widget = QTabWidget(self)
        self.addContentWidget(self.tab_widget)

        self.info_tab = DeviceInfoWidget(self)
        self.info_tab.updateInfo(bot)

        self.tasks_tab = DeviceTasksWidget(bot, self)

        self.shell_tab = ShellWidget(bot, self)

        self.tab_widget.addTab(self.info_tab, self.info_tab.tab_name)
        self.tab_widget.addTab(self.tasks_tab, self.tasks_tab.tab_name)
        self.tab_widget.addTab(self.shell_tab, self.shell_tab.tab_name)

        self.tasks_tab.stop_task.connect(self.stop_task.emit)
        self.tasks_tab.force_start_task.connect(self.force_start_task.emit)
        self.shell_tab.run_shell.connect(self.run_shell.emit)

    @Slot(list)
    def updateProperties(self, info):
        if self.isVisible():
            self.info_tab.updateInfo(info)

    @Slot(list)
    def updateTasks(self, tasks):
        if self.isVisible():
            self.tasks_tab.updateTasks(tasks)

    @Slot(int, str)
    def appendShell(self, device_id, output):
        if self.isVisible():
            self.shell_tab.on_shell_message_received(device_id, output)

    @Slot()
    def close(self):
        super().close()
        self.deleteLater()
