from qtpy.QtWidgets import QTabWidget
from qtpy.QtCore import Signal

from qasync import asyncSlot

from qrainbowstyle.windows import FramelessWindow
from .Widgets import DeviceInfoWidget, DeviceTasksWidget


class DeviceWindow(FramelessWindow):
    stop_task = Signal(int, int)

    def __init__(self, bot, parent):
        super(DeviceWindow, self).__init__(parent)

        self.tab_widget = QTabWidget(self)
        self.addContentWidget(self.tab_widget)

        self.info_tab = DeviceInfoWidget(self)
        self.info_tab.updateInfo(bot)

        self.tasks_tab = DeviceTasksWidget(bot, self)
        self.tab_widget.addTab(self.info_tab, self.info_tab.tab_name)
        self.tab_widget.addTab(self.tasks_tab, self.tasks_tab.tab_name)
        self.tasks_tab.stop_task.connect(self.stop_task.emit)

    @asyncSlot(list)
    async def updateProperties(self, info):
        if self.isVisible():
            self.info_tab.updateInfo(info)

    @asyncSlot(list)
    async def updateTasks(self, tasks):
        if self.isVisible():
            self.tasks_tab.updateTasks(tasks)

    @asyncSlot()
    async def close(self):
        super().close()
        self.deleteLater()
