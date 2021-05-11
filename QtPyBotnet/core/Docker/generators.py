from qtpy.QtCore import Slot, Signal, QObject, QProcess

import os
import sys
import signal
import string
import logging
import tempfile
from distutils.dir_util import copy_tree

docker_build_win = string.Template("cmd /c docker build -t ${TAG} -f ${DOCKERFILE} .")
docker_build_linux = string.Template("docker build -t ${TAG} -f ${DOCKERFILE} .")

docker_run_win = string.Template("cmd /c docker run --rm -v %cd%/:/src/ ${TAG} ${COMMAND}")
docker_run_linux = string.Template("docker run --rm -v $$(pwd)/:/src/ ${TAG} ${COMMAND}")


class BaseGenerator(QObject):
    build_progress = Signal(str)
    build_error = Signal(str)
    build_finished = Signal(int)
    build_started = Signal()

    tag = ""
    dockerfile = ""
    build_suffix = ""

    def __init__(self, parent=None):
        super(BaseGenerator, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__run_command = ""
        self.__build_process = None
        self.__run_process = None
        self.__finished = False
        self.__cancleded = False

    def setFinished(self, value):
        self.__finished = value

    def isFinished(self):
        return self.__finished

    @Slot(str)
    def start(self, run_command):
        self.__run_command = run_command
        self.docker_build()
        self.build_started.emit()

    @Slot()
    def stop(self):
        self.__cancleded = True
        if self.__build_process:
            self.__build_process.terminate()
            # os.kill(self.__build_process.processId(), signal.CTRL_C_EVENT)
        if self.__run_process:
            self.__run_process.terminate()
            # os.kill(self.__run_process.processId(), signal.CTRL_C_EVENT)

    @Slot()
    def docker_build(self):
        self.build_progress.emit("<GENERATOR> Starting Docker image build.")
        if sys.platform == "win32":
            command = docker_build_win
        else:
            command = docker_build_linux
        self.__build_process = QProcess(self)
        self.__build_process.setProcessChannelMode(QProcess.MergedChannels)
        self.__build_process.setWorkingDirectory("./core/Docker")
        self.__build_process.finished.connect(self.__on_docker_build_finished)
        self.__build_process.readyRead.connect(lambda: self.build_progress.emit(bytes(
            self.__build_process.readAll()).decode('mbcs')))
        self.__build_process.start(command.substitute(TAG=self.tag, DOCKERFILE=self.dockerfile))

    @Slot(str)
    def docker_run(self):
        self.build_progress.emit("<GENERATOR> Starting Docker run.")
        if sys.platform == "win32":
            command = docker_run_win
        else:
            command = docker_run_linux
        self.tmpdir = tempfile.TemporaryDirectory()
        copy_tree("./client/", self.tmpdir.name)
        self.build_progress.emit("<GENERATOR> Created temporary directory: {}".format(self.tmpdir.name))
        self.logger.info("Created temporary directory: {}".format(self.tmpdir.name))
        self.__run_process = QProcess(self)
        self.__run_process.setProcessChannelMode(QProcess.MergedChannels)
        self.__run_process.setWorkingDirectory(self.tmpdir.name)
        self.__run_process.finished.connect(self.__on_docker_run_finished)
        self.__run_process.readyRead.connect(lambda: self.build_progress.emit(bytes(
            self.__run_process.readAll()).decode('mbcs')))
        self.__run_process.start(command.substitute(TAG=self.tag,
                                 DOCKERFILE=self.dockerfile,
                                 COMMAND=self.__run_command))

    @Slot(int, QProcess.ExitStatus)
    def __on_docker_build_finished(self, exit_code, exit_status):
        if self.__cancleded:
            self.build_progress.emit("<GENERATOR> Skipping Docker run.")
            self.build_finished.emit(exit_code)
            self.__cleanup()
            return

        if exit_code == 0:
            self.build_progress.emit("<GENERATOR> Docker image building finished!")
            self.docker_run()
        else:
            self.build_progress.emit("<GENERATOR> Docker image building failed!")
            self.build_finished.emit(exit_code)

    @Slot(int, QProcess.ExitStatus)
    def __on_docker_run_finished(self, exit_code, exit_status):
        if exit_code == 0:
            copy_tree(os.path.join(self.tmpdir.name, "./dist/"), "./client/dist/")
        self.__cleanup()
        self.build_progress.emit("<GENERATOR> {} run finished with exit code {}".format(
            self.__class__.__name__, exit_code))
        self.build_finished.emit(exit_code)

    def __cleanup(self):
        try:
            self.tmpdir.cleanup()
            self.build_progress.emit("<GENERATOR> Cleanup successfull.")
        except Exception as e:
            self.build_progress.emit("<GENERATOR> Error while cleaning after build: {}".format(e))


class Win32Generator(BaseGenerator):
    tag = "qtpybotnet-win32"
    dockerfile = "Dockerfile-py3-win32"
    build_suffix = "-win32"


class Win64Generator(BaseGenerator):
    tag = "qtpybotnet-win64"
    dockerfile = "Dockerfile-py3-win64"
    build_suffix = "-win64"


class Amd64Generator(BaseGenerator):
    tag = "qtpybotnet-amd64"
    dockerfile = "Dockerfile-py3-amd64"
    build_suffix = "-amd64"


class i386Generator(BaseGenerator):
    tag = "qtpybotnet-i386"
    dockerfile = "Dockerfile-py3-i386"
    build_suffix = "-i386"
