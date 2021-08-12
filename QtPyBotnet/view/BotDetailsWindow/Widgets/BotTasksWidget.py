from qtpy.QtWidgets import (QWidget, QFormLayout, QMenu, QAction, QLabel, QHBoxLayout, QPlainTextEdit, QLineEdit,
                            QPushButton, QVBoxLayout, QListWidget, QListWidgetItem)
from qtpy.QtCore import Signal, Slot, Qt
from qtpy.QtGui import QCursor, QCloseEvent, QSyntaxHighlighter, QTextCharFormat

from models import Task, Bot
from models.EventsTable import TasksTableModel

from .TasksTableView import TasksTableView
from view.TaskDetailsWindow import TaskDetailsWindow


class TasksWidget(QWidget):
    """Shows tasks table."""
    stop_task = Signal(Bot, Task)
    force_start_task = Signal(Bot, Task)

    def __init__(self, bot, parent):
        super(TasksWidget, self).__init__(parent)
        self.bot = bot

        self.menu = None
        self.task_details_window = None

        self.widget_layout = QHBoxLayout(self)
        self.setLayout(self.widget_layout)
        self.table = TasksTableView(self)
        self.table.context_menu_requested.connect(self.show_context_menu)
        self.table.task_double_clicked.connect(self.create_task_details_window)
        self.model = TasksTableModel(self)
        self.model.setBot(bot)
        self.table.setModel(self.model)
        self.widget_layout.addWidget(self.table)

    @Slot(list)
    def update_tasks(self, data):
        self.model.setEvents(data)

    @Slot(Task)
    def create_task_details_window(self, task: Task):
        self.task_details_window = TaskDetailsWindow(self)
        self.task_details_window.setTask(task)
        self.task_details_window.show()

    @Slot(int)
    def show_context_menu(self, task_id) -> None:
        self.menu = QMenu(self)
        force_start_action = QAction('Force start', self)
        force_start_action.triggered.connect(lambda: self.on_force_start_action_triggered(task_id))

        stop_action = QAction('Stop', self)
        stop_action.triggered.connect(lambda: self.on_stop_action_triggered(task_id))
        self.menu.addAction(force_start_action)
        self.menu.addAction(stop_action)
        self.menu.popup(QCursor.pos())

    @Slot(int)
    def on_force_start_action_triggered(self, task_id):
        task = self.table.model().getEventById(task_id)
        if task:
            self.force_start_task.emit(self.bot, task)

    @Slot(int)
    def on_stop_action_triggered(self, task_id):
        task = self.table.model().getEventById(task_id)
        if task:
            self.stop_task.emit(self.bot, task)
