import os

from qtpy.QtCore import Slot, Signal, QObject

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

    tag = ""
    dockerfile = ""
    build_suffix = ""

    def __init__(self, command):
        super(BaseGenerator, self).__init__(parent=None)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__build_process = None
        self.__run_process = None
        self.__finished = False
        self.__cancleded = False
        self.__run_command = command
        self.tmpdir = None

    def setFinished(self, value):
        self.__finished = value

    def isFinished(self):
        return self.__finished

    @Slot()
    def start(self):
        self.build_started.emit()
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
        self.build_progress.emit("<GENERATOR> Starting Docker image build.")
        client = docker.from_env()
        resp = client.api.build(path="./core/Docker", dockerfile=self.dockerfile, tag=self.tag, quiet=False)
        if isinstance(resp, str):
            return self.docker_run(client.images.get(resp))
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

    @Slot(str)
    def docker_run(self, image_id: str):
        if self.__cancleded:
            self.build_progress.emit("<GENERATOR> Skipping Docker run")
            self.__cleanup()
            return

        self.tmpdir = tempfile.TemporaryDirectory()
        copy_tree("./client/", self.tmpdir.name)

        client = docker.from_env()
        container = client.api.create_container(image_id, self.__run_command, detach=True,
                                                volumes=['/src/'],
                                                host_config=client.api.create_host_config(binds=[
                                                    '{}:/src/'.format(self.tmpdir.name)
                                                ]))
        container = client.containers.get(container['Id'])
        container.start()

        logs = container.attach(stdout=True, stderr=True, stream=True, logs=True)
        for log in logs:
            self.build_progress.emit(str(log, encoding="utf-8"))

        keep_build = True
        exit_status = container.wait()['StatusCode']
        if exit_status == 0:
            if keep_build:
                copy_tree(os.path.normpath(self.tmpdir.name), os.path.join("./client/dist/", self.dockerfile))
            else:
                copy_tree(os.path.normpath(os.path.join(self.tmpdir.name, "./dist/")), "./client/dist/")
        else:
            self.build_error.emit(str(container.logs(stdout=False, stderr=True), encoding="utf-8"))
        self.__cleanup()
        self.__finished = True
        self.build_finished.emit(exit_status)

    def __cleanup(self):
        try:
            if self.tmpdir:
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
