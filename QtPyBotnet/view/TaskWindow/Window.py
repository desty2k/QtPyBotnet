from qtpy.QtCore import Signal

from qrainbowstyle.windows import FramelessWindow

from view.TaskWindow.Widgets import MainTaskWidget


class TaskWindow(FramelessWindow):
    send_task = Signal(int, str, dict, int)

    def __init__(self, parent):
        super(TaskWindow, self).__init__(parent)
        self.radios = []

        self.content_widget = MainTaskWidget(self)
        self.content_widget.send_task.connect(self.send_task.emit)
        self.addContentWidget(self.content_widget)
