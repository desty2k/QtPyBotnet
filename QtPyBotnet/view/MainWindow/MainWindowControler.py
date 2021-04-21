import logging

from qtpy.QtCore import QMetaObject, Signal, Qt
from qtpy.QtWidgets import QDialogButtonBox

from qrainbowstyle.windows import FramelessWindow, FramelessQuestionMessageBox, FramelessCriticalMessageBox
from qrainbowstyle.widgets import WaitingSpinner
from qrainbowstyle.utils import StyleLooper

from qasync import asyncSlot

from models import Bot
from core.Network import GUIClient
from view.TaskWindow import TaskWindow
from view.ConsoleWindow import Console
from view.MainWindow import TitlebarMenu, MainWidget
from view.DeviceWindow import DeviceWindow


class MainWindow(FramelessWindow):
    """Main window controler manages signals and GUI IO."""
    gui_connected = Signal()
    gui_connect_fail = Signal(str)
    gui_disconnected = Signal()
    gui_retry_connect = Signal()
    closeAccepted = Signal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.client = GUIClient()
        self.content_widget = None

        # windows and widgets
        self.task_window = None
        self.device_window = None
        self.console = None
        self.spinner = None
        self.menu = None

        self.styler = StyleLooper()
        self.resize(1200, 700)

        try:
            self.closeClicked.disconnect()
        except Exception:  # noqa
            pass
        self.closeClicked.connect(self.on_closeClicked)

    @asyncSlot()
    async def setup_gui(self, config):
        self.content_widget = MainWidget(self)
        self.content_widget.bot_double_clicked.connect(self.on_bot_double_clicked)
        self.content_widget.task_button_clicked.connect(self.on_task_button_clicked)
        self.content_widget.setupUi(config)
        self.addContentWidget(self.content_widget)

        self.console = Console(self)
        self.console.message.connect(self.client.write)
        self.console.setVisible(False)

        self.spinner = WaitingSpinner(self, disableParentWhenSpinning=True,
                                      modality=Qt.WindowModal,
                                      centerOnParent=True)
        self.spinner.start()

        self.menu = TitlebarMenu(self)
        self.addMenu(self.menu)
        QMetaObject.connectSlotsByName(self)

    @asyncSlot()
    async def on_task_button_clicked(self):
        self.task_window = TaskWindow(self)
        self.task_window.show()

    @asyncSlot(Bot)
    async def on_bot_double_clicked(self, bot: Bot):
        self.device_window = DeviceWindow(bot, self)
        self.device_window.toggle_module.connect(self.client.toggle_module)
        self.device_window.stop_task.connect(self.client.stop_task)
        self.device_window.show()

    @asyncSlot(str, int, str)
    async def connect_to_gui_server(self, ip, port, key):
        self.client.connected.connect(self.gui_connected.emit)
        self.client.connected.connect(self.spinner.stop)
        self.client.failed_to_connect.connect(self.gui_connect_fail.emit)
        self.client.message.connect(self.on_gui_message)
        self.client.disconnected.connect(self.gui_disconnected.emit)
        self.start_gui_client(ip, port, key)

    @asyncSlot(str, int, str)
    async def start_gui_client(self, ip, port, key):
        self.client.start(ip, port, key)

    @asyncSlot()
    async def on_show_console_triggered(self):
        self.console.show()

    @asyncSlot()
    async def on_change_style_triggered(self):
        self.styler.change()

    @asyncSlot(bool)
    async def on_stay_top_action_triggered(self, checked):
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    @asyncSlot(dict)
    async def on_gui_message(self, message: dict):
        """Triggered when GUI client receive message from GUI server."""
        self.console.write(message)
        bot_id = message.get("bot_id")

        if bot_id:
            event_type = message.get("event_type")
            if event_type == "connection":
                event = message.get("event")

                if event == "connected":
                    self.content_widget.add_bot(bot_id,
                                                message.get("ip"),
                                                message.get("port"))
                elif event == "disconnected":
                    self.content_widget.remove_bot(bot_id)

            elif event_type in ("info", "module", "task"):
                self.content_widget.update_bot(bot_id, message)

    @asyncSlot(str)
    async def on_gui_connect_fail(self, message):
        self.spinner.stop()
        self.setEnabled(False)
        self.warning_dialog = FramelessCriticalMessageBox(self)
        self.warning_dialog.setWindowModality(Qt.WindowModal)
        self.warning_dialog.setStandardButtons(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.warning_dialog.button(QDialogButtonBox.No).clicked.connect(self.closeAccepted.emit)
        self.warning_dialog.button(QDialogButtonBox.Yes).clicked.connect(self.gui_retry_connect.emit)
        self.warning_dialog.button(QDialogButtonBox.Yes).clicked.connect(self.warning_dialog.close)
        self.warning_dialog.setText("Failed to connect to GUI server. Do you want to retry?")
        self.warning_dialog.show()

    @asyncSlot()
    async def on_closeClicked(self):
        self.close_dialog = FramelessQuestionMessageBox(self)
        self.close_dialog.setWindowModality(Qt.WindowModal)
        self.close_dialog.setStandardButtons(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.close_dialog.button(QDialogButtonBox.No).clicked.connect(self.close_dialog.close)
        self.close_dialog.button(QDialogButtonBox.Yes).clicked.connect(self.closeAccepted.emit)
        self.close_dialog.button(QDialogButtonBox.Yes).clicked.connect(self.close_dialog.close)
        self.close_dialog.setText("Do you want to close app?")
        self.close_dialog.show()

    @asyncSlot()
    async def close(self):
        if self.client:
            self.client.close()
            self.client.wait()
        super().close()
