import os
import re
import base64
import string
import logging

from qtpy.QtCore import QObject, Signal, Slot, QThread

from core.Docker import *
from models.Device import Device

PACK_COMMAND = string.Template(
    "\"pyarmor pack client.py -n $name -e \'$pyinstaller_kwargs\' -x \'$pyarmor_kwargs\'\"")

PYARMOR_PYINSTALLER_KWARGS = string.Template(" -F --exclude-module shiboken2 --exclude-module PyQt5 "
                                             "--exclude-module PySide2 --exclude-module _tkinter "
                                             "--exclude-module tkinter --exclude-module Tkinter "
                                             "--exclude-module tcl --exclude-module tk --exclude-module FixTk "
                                             "--exclude-module qtpy -i $icon -w ")

PYARMOR_OBFUSCATE_KWARGS = " --restrict 2 --advanced 2 --wrap-mode 1 -r "


class ClientBuilder(QObject):
    build_options = Signal(Device, dict)
    build_stopped = Signal(Device)
    build_error = Signal(Device, str)
    build_finished = Signal(Device)

    generator_started = Signal(Device, str)
    generator_progress = Signal(Device, str, str)
    generator_finished = Signal(Device, str, int)

    def __init__(self):
        super(ClientBuilder, self).__init__()
        self.generators = [i386Generator, Amd64Generator, Win32Generator, Win64Generator]

        self.device = None
        self.running_builders = []
        self.logger = logging.getLogger(self.__class__.__name__)

    @Slot(Device, str, str, list)
    def start(self, device, name, icon, builders):
        if self.device or self.running_builders:
            self.build_error.emit(device, "Build in progress!")
            return

        if not os.path.exists(os.path.join("./client/resources/", icon)):
            self.build_error.emit(device, "Icon does not exist!")
            return
        else:
            icon = os.path.join("./resources/", icon)

        if not name:
            self.build_error.emit(device, "Script name is not valid!")
            return

        name = str(name)
        if not re.fullmatch("^[0-9a-zA-Z_\-. ]+$", name):  # noqa
            self.build_error.emit(device, "Script name contains a disallowed characters!")
            return

        try:
            from docker import from_env
            from_env()
        except Exception as e:
            self.build_error.emit(device, "Failed to start Docker service: {}".format(e))
            return

        try:
            if not os.path.exists("./build/"):
                os.makedirs("./build/", exist_ok=True)
        except Exception as e:
            self.build_error.emit(device, "Failed to create build directory: {}".format(e))
            return

        pyinstaller_kwargs = PYARMOR_PYINSTALLER_KWARGS.substitute(icon=icon)

        for generator in self.generators:
            if generator.__name__ in builders:
                command = PACK_COMMAND.substitute(pyinstaller_kwargs=pyinstaller_kwargs,
                                                  pyarmor_kwargs=PYARMOR_OBFUSCATE_KWARGS,
                                                  name=name + generator.build_suffix)
                gen_obj = generator(command)
                gen_obj.build_update.connect(lambda progress, dev=device, gen_name=generator.__name__:
                                             self.generator_progress.emit(dev, gen_name,
                                                                          "<INFO> " + progress))
                gen_obj.build_error.connect(lambda progress, dev=device, gen_name=generator.__name__:
                                            self.generator_progress.emit(dev, gen_name,
                                                                         "<ERROR> " + progress))
                gen_obj.build_progress.connect(lambda progress, dev=device, gen_name=generator.__name__:
                                               self.generator_progress.emit(dev, gen_name, progress))
                gen_obj.build_finished.connect(lambda exit_code, dev=device, gen_name=generator.__name__:
                                               self.on_generator_finished(dev, gen_name, exit_code))
                gen_obj.build_started.connect(lambda dev=device, gen_name=generator.__name__:
                                              self.generator_started.emit(dev, gen_name))
                thread = QThread()
                thread.started.connect(gen_obj.start)
                gen_obj.moveToThread(thread)
                self.running_builders.append((gen_obj, thread))
        for gen, thr in self.running_builders:
            self.logger.info("Starting {} generator".format(gen.dockerfile))
            thr.start()

    @Slot(Device, str, int)
    def on_generator_finished(self, device, gen_name, exit_code):
        for generator in self.running_builders:
            if generator.__class__.__name__ == gen_name:
                generator.setFinished(True)
        self.generator_finished.emit(device, gen_name, exit_code)
        if all(gen.isFinished() for gen, thr in self.running_builders):
            self.device = None
            self.build_finished.emit(device)

    @Slot(Device)
    def stop(self, device):
        for gen, thr in self.running_builders:
            gen.stop()
        self.running_builders.clear()
        self.build_stopped.emit(device)

    @Slot(Device)
    def get_options(self, device):
        options = {"icons": [], "generators": []}
        try:
            for file_name in os.listdir("./client/resources/"):
                if file_name.endswith(".ico"):
                    with open(os.path.join("./client/resources/", file_name), "rb") as f:
                        options["icons"].append({"name": file_name, "ico": base64.b64encode(f.read()).decode()})
        except Exception as e:
            self.build_error.emit(device, "Failed to get available icons: {}".format(e))
            return
        for generator in self.generators:
            options["generators"].append(generator.__name__)
        self.build_options.emit(device, options)

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
