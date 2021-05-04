import base64
import logging

from qtpy.QtCore import Signal, Slot, Qt
from qtpy.QtGui import QIcon, QPixmap
from qtpy.QtWidgets import QVBoxLayout, QPushButton, QWidget, QDialogButtonBox, QListWidget, QComboBox, \
    QLineEdit, QListWidgetItem, QMenu, QAction

from qrainbowstyle.widgets import WaitingSpinner
from qrainbowstyle.windows import FramelessWindow, FramelessCriticalMessageBox, FramelessInformationMessageBox, \
    FramelessQuestionMessageBox

from view.PayloadWindow.ProgressWindow import ProgressWindow


class PayloadWindow(FramelessWindow):
    get_build_options = Signal()
    start_build = Signal(str, str, list)
    stop_build = Signal()

    def __init__(self, parent):
        super(PayloadWindow, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.progress_windows = []

        self.content_widget = QWidget(self)
        self.addContentWidget(self.content_widget)

        self.widget_layout = QVBoxLayout(self.content_widget)
        self.content_widget.setLayout(self.widget_layout)

        self.spinner = WaitingSpinner(self, parent, modality=Qt.WindowModal,
                                      roundness=70.0, fade=70.0, radius=15.0, lines=6,
                                      line_length=25.0, line_width=4.0, speed=1.0)

        self.build_name_edit = QLineEdit(self)
        self.icon_combobox = QComboBox(self)
        self.generators_list = QListWidget(self)
        self.build_button = QPushButton("Build", self)
        self.build_button.clicked.connect(self.on_build_button_clicked)

        self.widget_layout.addWidget(self.build_name_edit)
        self.widget_layout.addWidget(self.icon_combobox)
        self.widget_layout.addWidget(self.generators_list)
        self.widget_layout.addWidget(self.build_button)

        self.menu = QMenu(self)
        self.menu.setTitle("Payload")
        self.reload_action = QAction(self.menu)
        self.reload_action.setText("Reload options")
        self.reload_action.triggered.connect(self.setupUi)
        self.menu.addAction(self.reload_action)
        self.addMenu(self.menu)

    def setupUi(self):
        self.spinner.start()
        self.get_build_options.emit()

    @Slot(dict)
    def process_build_message(self, message):
        if self.isVisible():
            event = message.get("event")
            if event == "options":
                options = message.get("options")
                self.set_options(options.get("generators"),
                                 options.get("icons"))
            elif event == "started":
                self.set_started(message.get("generator_name"))
            elif event == "stopped":
                self.set_stopped()
            elif event == "progress":
                self.set_progress(message.get("generator_name"),
                                  message.get("progress"))
            elif event == "error":
                self.set_error(message.get("error"))
            elif event == "generator_finished":
                self.set_generator_finished(message.get("generator_name"),
                                            message.get("exit_code"))
            elif event == "build_finished":
                self.set_build_finished()

    def set_progress(self, generator_name, progress):
        for win in self.progress_windows:
            if win.generator() == generator_name:
                win.appendProgress(progress)

    def set_started(self, generator_name):
        win = ProgressWindow(self, generator_name)
        win.show()
        self.progress_windows.append(win)
        self.logger.info("Generator {} started!".format(generator_name))
        self.reload_action.setEnabled(False)
        self.spinner.start()

    def set_generator_finished(self, generator_name, exit_code):
        self.logger.info("Generator {} finished with exit code {}.".format(generator_name, exit_code))

    def set_options(self, generators, icons):
        self.build_name_edit.clear()
        self.generators_list.clear()
        self.icon_combobox.clear()
        for generator in generators:
            item = QListWidgetItem(generator, self.generators_list)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.generators_list.addItem(item)
        for icon in icons:
            name = icon.get("name")
            pix = QPixmap()
            pix.loadFromData(base64.b64decode(icon.get("ico")))
            ico = QIcon()
            ico.addPixmap(pix)
            self.icon_combobox.addItem(ico, name)
        self.spinner.stop()

    def set_stopped(self):
        self.on_build_finished()
        self.build_button.setText("Build")
        self.stopped_messagebox = FramelessInformationMessageBox(self)
        self.stopped_messagebox.setText("Build process has been stopped successfully.")
        self.stopped_messagebox.setStandardButtons(QDialogButtonBox.Ok)
        self.stopped_messagebox.button(QDialogButtonBox.Ok).clicked.connect(self.stopped_messagebox.close)
        self.stopped_messagebox.show()

    def set_error(self, error):
        self.on_build_finished()
        self.build_button.setText("Build")
        self.error_messagebox = FramelessCriticalMessageBox(self)
        self.error_messagebox.setText(error)
        self.error_messagebox.setStandardButtons(QDialogButtonBox.Ok)
        self.error_messagebox.button(QDialogButtonBox.Ok).clicked.connect(self.error_messagebox.close)
        self.error_messagebox.show()

    def set_build_finished(self):
        self.on_build_finished()
        self.build_button.setText("Build")
        self.build_finished_messagebox = FramelessInformationMessageBox(self)
        self.build_finished_messagebox.setText("Build process has been finished.")
        self.build_finished_messagebox.setStandardButtons(QDialogButtonBox.Ok)
        self.build_finished_messagebox.button(QDialogButtonBox.Ok).clicked.connect(self.build_finished_messagebox.close)
        self.build_finished_messagebox.show()

    @Slot()
    def on_build_button_clicked(self):
        if self.build_button.text() == "Build":
            generators = []
            for i in range(self.generators_list.count()):
                item = self.generators_list.item(i)
                if item.checkState() == Qt.Checked:
                    generators.append(item.text())
            self.start_build.emit(self.build_name_edit.text(), self.icon_combobox.currentText(), generators)
            self.build_button.setText("Stop")
        else:
            self.stop_build_messagebox = FramelessQuestionMessageBox(self)
            self.stop_build_messagebox.setText("Do you want to stop build process?")
            self.stop_build_messagebox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            self.stop_build_messagebox.button(QDialogButtonBox.Cancel).clicked.connect(self.stop_build_messagebox.close)
            self.stop_build_messagebox.button(QDialogButtonBox.Ok).clicked.connect(self.stop_build.emit)
            self.stop_build_messagebox.button(QDialogButtonBox.Ok).clicked.connect(self.stop_build_messagebox.close)
            self.stop_build_messagebox.show()

    def on_build_finished(self):
        self.reload_action.setEnabled(True)
        self.spinner.stop()
