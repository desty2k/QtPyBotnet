from qtpy.QtWidgets import (QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QMenu, QAction)
from qtpy.QtCore import Slot, Signal
from qtpy.QtGui import QCursor

from models import Module, Bot
from models.ModulesTableModel import ModulesTableModel
from view.ModuleDetailsWindow import ModuleDetailsWindow
from .ModulesTableView import ModulesTableView


class ModulesWidget(QWidget):
    """Widget with table with Python modules loaded on bot."""
    unload_module = Signal(Bot, Module)

    def __init__(self, bot, parent):
        super(ModulesWidget, self).__init__(parent)
        self.bot = bot

        self.menu = None
        self.module_code_window = None

        self.widget_layout = QHBoxLayout(self)
        self.setLayout(self.widget_layout)

        self.table = ModulesTableView(self)
        self.table.context_menu_requested.connect(self.show_context_menu)
        self.table.module_double_clicked.connect(self.create_module_details_window)

        self.model = ModulesTableModel(self)
        self.model.setBot(bot)
        self.table.setModel(self.model)

        self.widget_layout.addWidget(self.table)

    @Slot(list)
    def update_tasks(self, data):
        self.model.setEvents(data)

    @Slot(Module)
    def create_module_details_window(self, module: Module):
        self.module_code_window = ModuleDetailsWindow(self)
        self.module_code_window.set_module(module)
        self.module_code_window.show()

    @Slot(str)
    def show_context_menu(self, module_name) -> None:
        self.menu = QMenu(self)
        unload_action = QAction("Unload", self)
        unload_action.triggered.connect(lambda: self.on_unload_action_triggered(module_name))
        self.menu.addAction(unload_action)
        self.menu.popup(QCursor.pos())

    @Slot(str)
    def on_unload_action_triggered(self, module_name):
        module = self.table.model().getModuleByName(module_name)
        if module:
            self.unload_module.emit(self.bot, module)
