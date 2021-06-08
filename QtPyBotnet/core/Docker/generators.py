from qtpy.QtCore import Slot, Signal, QObject

import os
import re
import docker
import logging
import tempfile
import itertools

from distutils.dir_util import copy_tree
from docker.utils.json_stream import json_stream
from docker.errors import BuildError

__all__ = ["i386Generator", "Amd64Generator", "Win32Generator", "Win64Generator"]


class BaseGenerator(QObject):
    build_progress = Signal(str)
    build_error = Signal(str)
    build_finished = Signal(int)
    build_started = Signal()
    build_update = Signal(str)

    tag = ""
    dockerfile = ""
    build_suffix = ""

    def __init__(self, command, keep_build=False):
        super(BaseGenerator, self).__init__(parent=None)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__build_process = None
        self.__run_process = None
        self.__finished = False
        self.__cancleded = False
        self.__tmpdir = None
        self.__client = None
        self.__run_command = command
        self.__keep_build = keep_build

    def setFinished(self, value):
        self.__finished = value

    def isFinished(self):
        return self.__finished

    @Slot()
    def start(self):
        self.build_started.emit()
        try:
            self.__client = docker.from_env()
        except Exception as e:
            self.build_error.emit("Failed to create Docker client: {}".format(e))
            self.build_finished.emit(100)
        self.docker_build()

    @Slot()
    def stop(self):
        self.__cancleded = True
        if self.__build_process:
            self.__build_process.terminate()
        if self.__run_process:
            self.__run_process.terminate()

    @Slot()
    def docker_build(self):
        self.build_update.emit("Starting Docker image build.")
        try:
            resp = self.__client.api.build(path="./core/Docker", dockerfile=self.dockerfile, tag=self.tag, quiet=False)
            if isinstance(resp, str):
                return self.docker_run(self.__client.images.get(resp))
            last_event = None
            image_id = None
            result_stream, internal_stream = itertools.tee(json_stream(resp))
            for chunk in internal_stream:
                if 'error' in chunk:
                    self.build_error.emit(chunk['error'])
                    raise BuildError(chunk['error'], result_stream)
                if 'stream' in chunk:
                    self.build_progress.emit(chunk['stream'])
                    match = re.search(
                        r'(^Successfully built |sha256:)([0-9a-f]+)$',
                        chunk['stream']
                    )
                    if match:
                        image_id = match.group(2)
                last_event = chunk
            if image_id:
                return self.docker_run(image_id)
            raise BuildError(last_event or 'Unknown', result_stream)
        except Exception as e:
            self.build_error.emit("An exception occurred while starting Docker image building process: {}".format(e))
            self.build_finished.emit(1)
            return

    @Slot(str)
    def docker_run(self, image_id: str):
        if self.__cancleded:
            self.build_update.emit("Skipping Docker run")
            self.cleanup()
            self.build_finished.emit(0)
            return

        try:
            # create temporary directory and copy client source code
            self.__tmpdir = tempfile.TemporaryDirectory()
            copy_tree("./client/", self.__tmpdir.name)
            self.build_update.emit("Created temporary directory: {}".format(self.__tmpdir.name))
            self.build_update.emit("Temporary directory contents: {}".format(os.listdir(self.__tmpdir.name)))
        except Exception as e:
            self.build_error.emit("Failed to create temporary directory: {}".format(e))

        try:
            # create and run container
            self.build_update.emit("Creating Docker container from image: {}".format(image_id))
            container = self.__client.api.create_container(image_id, self.__run_command, detach=True,
                                                           volumes=['/src/'],
                                                           host_config=self.__client.api.create_host_config(binds=[
                                                               '{}:/src/:rw'.format(self.__tmpdir.name)
                                                           ]))
            container = self.__client.containers.get(container['Id'])
            self.build_update.emit("Starting Docker container")
            container.start()
            self.build_update.emit("Started building process")

            # send container logs
            logs = container.attach(stdout=True, stderr=True, stream=True, logs=True)
            for log in logs:
                self.build_progress.emit(str(log, encoding="utf-8"))

            exit_status = container.wait()['StatusCode']
            if exit_status == 0:
                self.build_update.emit("Build process completed successfully")
                if self.__keep_build:
                    output_path = copy_tree(os.path.normpath(self.__tmpdir.name), os.path.join("./client/dist/", self.dockerfile))
                else:
                    output_path = copy_tree(os.path.normpath(os.path.join(self.__tmpdir.name, "./dist/")), "./client/dist/")
                self.build_update.emit("Executable path: {}".format(output_path))
            else:
                self.build_error.emit(str(container.logs(stdout=False, stderr=True), encoding="utf-8"))
        except Exception as e:
            exit_status = 1
            self.build_error.emit("An exception occurred while starting Docker container: {}".format(e))

        self.cleanup()
        self.setFinished(True)
        self.build_update.emit("{} completed with exit code {}".format(self.dockerfile, exit_status))
        self.build_finished.emit(exit_status)

    @Slot()
    def cleanup(self):
        try:
            if self.__tmpdir:
                self.__tmpdir.cleanup()
            self.build_update.emit("Cleanup successfull.")
        except Exception as e:
            self.build_error.emit("Error while cleaning after build: {}".format(e))


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
