import os
import re
import json
import base64
import string
import logging

from qtpy.QtCore import QObject, Signal, Slot, QThread

from core.Docker import *

PACK_COMMAND = string.Template(
    "\"pyarmor pack client.py -n $name -e \'$pyinstaller_kwargs\' -x \'$pyarmor_kwargs\'\"")

PYARMOR_PYINSTALLER_KWARGS = string.Template(" -F --exclude-module shiboken2 --exclude-module PyQt5 "
                                             "--exclude-module PySide2 --exclude-module _tkinter "
                                             "--exclude-module tkinter --exclude-module Tkinter "
                                             "--exclude-module tcl --exclude-module tk --exclude-module FixTk "
                                             "--exclude-module qtpy -i $icon -w ")

PYARMOR_OBFUSCATE_KWARGS = " --restrict 2 --advanced 2 --wrap-mode 1 -r "


class ClientBuilder(QObject):
    build_options = Signal(int, dict)
    build_stopped = Signal(int)
    build_error = Signal(int, str)
    build_finished = Signal(int)

    generator_started = Signal(int, str)
    generator_progress = Signal(int, str, str)
    generator_finished = Signal(int, str, int)

    def __init__(self):
        super(ClientBuilder, self).__init__()
        self.generators = [i386Generator, Amd64Generator, Win32Generator, Win64Generator]
        self.running_builders = []
        self.logger = logging.getLogger(self.__class__.__name__)

    @Slot(int, str, str, list)
    def start(self, device_id, name, icon, builders):
        if self.running_builders:
            self.build_error.emit(device_id, "Build in progress!")
            return

        if not os.path.exists(os.path.join("./client/resources/", icon)):
            self.build_error.emit(device_id, "Icon does not exist!")
            return
        else:
            icon = os.path.join("./resources/", icon)

        if not name:
            self.build_error.emit(device_id, "Script name is not valid!")
            return

        name = str(name)
        if not re.fullmatch("^[0-9a-zA-Z_\-. ]+$", name):  # noqa
            self.build_error.emit(device_id, "Script name contains a disallowed characters!")
            return

        try:
            from docker import from_env
            from_env()
        except Exception as e:
            self.build_error.emit(device_id, "Failed to start Docker service: {}".format(e))
            return

        pyinstaller_kwargs = PYARMOR_PYINSTALLER_KWARGS.substitute(icon=icon)

        for generator in self.generators:
            if generator.__name__ in builders:
                command = PACK_COMMAND.substitute(pyinstaller_kwargs=pyinstaller_kwargs,
                                                  pyarmor_kwargs=PYARMOR_OBFUSCATE_KWARGS,
                                                  name=name + generator.build_suffix)
                gen_obj = generator(command)
                gen_obj.build_progress.connect(lambda progress, dev_id=device_id, gen_name=generator.__name__:
                                               self.generator_progress.emit(dev_id, gen_name, progress))
                gen_obj.build_finished.connect(lambda exit_code, dev_id=device_id, gen_name=generator.__name__:
                                               self.on_generator_finished(dev_id, gen_name, exit_code))
                gen_obj.build_started.connect(lambda dev_id=device_id, gen_name=generator.__name__:
                                              self.generator_started.emit(dev_id, gen_name))
                thread = QThread()
                thread.started.connect(gen_obj.start)
                gen_obj.moveToThread(thread)
                self.running_builders.append((gen_obj, thread))
        for gen, thr in self.running_builders:
            self.logger.info("Starting {} generator".format(gen.dockerfile))
            thr.start()

    @Slot(int, str, int)
    def on_generator_finished(self, device_id, gen_name, exit_code):
        for generator in self.running_builders:
            if generator.__class__.__name__ == gen_name:
                generator.setFinished(True)
        self.generator_finished.emit(device_id, gen_name, exit_code)
        if all(gen.isFinished() for gen, thr in self.running_builders):
            self.build_finished.emit(device_id)

    @Slot(int)
    def stop(self, device_id):
        for gen, thr in self.running_builders:
            gen.stop()
        self.running_builders.clear()
        self.build_stopped.emit(device_id)

    @Slot(int)
    def get_options(self, device_id):
        options = {"icons": [], "generators": []}
        try:
            for file_name in os.listdir("./client/resources/"):
                if file_name.endswith(".ico"):
                    with open(os.path.join("./client/resources/", file_name), "rb") as f:
                        options["icons"].append({"name": file_name, "ico": base64.b64encode(f.read()).decode()})
        except Exception as e:
            self.build_error.emit(device_id, "Failed to get available icons: {}".format(e))
            return
        for generator in self.generators:
            options["generators"].append(generator.__name__)
        self.build_options.emit(device_id, options)

    @Slot()
    def patch_win10toast(self):
        from pathlib import Path
        from distutils.sysconfig import get_python_lib
        hooks_path = Path(get_python_lib()) / "Pyinstaller" / "hooks"
        if not hooks_path.exists():
            self.build_error.emit("Failed to find Pyinstaller hooks directory")
            return
        hooks_path = hooks_path / "hook-win10toast.py"
        with open(hooks_path, "w+") as f:
            f.write("from PyInstaller.utils.hooks import copy_metadata\n\ndatas = copy_metadata('win10toast')")
