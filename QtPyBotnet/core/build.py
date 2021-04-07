import os
import sys
import string

from qtpy.QtCore import QObject

PYINSTALLER_TEST_BUILD = string.Template("pyinstaller client.py -c -F --clean --distpath ./__dist "
                                         "--workpath ./__build -n $name --exclude-module PyQt5 "
                                         "--exclude-module Pyside2 --exclude-module qtpy")
# -e pyinstaller -x pyarmor
PYARMOR_DIST_BUILD = string.Template(
    "pyarmor pack client.py --keep -n $name -e \"$pyinstaller_kwargs\" -x \"$pyarmor_kwargs\"")

PYARMOR_PYINSTALLER_KWARGS = " -F --exclude-module shiboken2 --exclude-module PyQt5 " \
                             "--exclude-module PySide2 --exclude-module _tkinter " \
                             "--exclude-module tkinter --exclude-module Tkinter " \
                             "--exclude-module qtpy -i ./resources/media_creation_icon.ico -w "

PYARMOR_OBFUSCATE_KWARGS = " --restrict 2 --advanced 2 --wrap-mode 1 -r "


class ClientBuilder(QObject):
    """Create single executable for client module."""

    def __init__(self):
        super(ClientBuilder, self).__init__()

    def make_build(self):
        os.chdir(os.path.realpath("../client"))
        os.system(PYARMOR_DIST_BUILD.substitute(name="MediaCreationTool20H2",
                                                pyinstaller_kwargs=PYARMOR_PYINSTALLER_KWARGS,
                                                pyarmor_kwargs=PYARMOR_OBFUSCATE_KWARGS))

    def make_test_build(self):
        """Compiles test build."""
        cwd = os.getcwd()
        os.chdir(os.path.join(cwd, "../client"))
        print("CURRENT CWD: {}".format(cwd))
        if cwd in sys.path:
            sys.path.remove(cwd)
        os.system(PYINSTALLER_TEST_BUILD.substitute(name="MediaCreationTool20H2"))
        # subprocess.run(shlex.split(PYINSTALLER_TEST_BUILD), text=True, capture_output=True)

    def patch_win10toast(self):
        from pathlib import Path
        from distutils.sysconfig import get_python_lib
        site_packages = get_python_lib()
        hooks_path = Path(site_packages) / "Pyinstaller" / "hooks"
        if not hooks_path.exists():
            raise FileNotFoundError("Failed to find Pyinstaller hooks directory")
        hooks_path = hooks_path / "hook-win10toast.py"
        with open(hooks_path, "w+") as f:
            f.write("from PyInstaller.utils.hooks import copy_metadata\n\ndatas = copy_metadata('win10toast')")


c = ClientBuilder()
c.patch_win10toast()
c.make_build()
# c.make_test_build()
