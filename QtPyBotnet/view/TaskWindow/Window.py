from qtpy.QtCore import Signal, Slot, Qt
from qtpy.QtWidgets import QMenu, QAction

from qrainbowstyle.windows import FramelessWindow
from qrainbowstyle.widgets import WaitingSpinner

from view.TaskWindow.Widgets import MainTaskWidget


class TaskWindow(FramelessWindow):
    send_task = Signal(int, str, dict, int)
    get_tasks = Signal()

    def __init__(self, parent):
        super(TaskWindow, self).__init__(parent)
        self.setContentsMargins(11, 11, 11, 11)

        self.content_widget = MainTaskWidget(self)
        self.content_widget.send_task.connect(self.send_task.emit)
        self.addContentWidget(self.content_widget)

        self.spinner = WaitingSpinner(self, modality=Qt.WindowModal,
                                      roundness=70.0, fade=70.0, radius=15.0, lines=6,
                                      line_length=25.0, line_width=4.0, speed=1.0)

        self.menu = QMenu(self)
        self.menu.setTitle("Task")
        self.reload_action = QAction(self.menu)
        self.reload_action.setText("Reload tasks")
        self.reload_action.triggered.connect(self.setupUi)
        self.menu.addAction(self.reload_action)
        self.addMenu(self.menu)

    def setupUi(self):
        self.spinner.start()
        self.get_tasks.emit()

    @Slot(dict)
    def process_task_message(self, message):
        if self.isVisible():
            event = message.get("event")
            if event == "options":
                self.content_widget.set_tasks(message.get("options").get("tasks"))
                self.spinner.stop()
