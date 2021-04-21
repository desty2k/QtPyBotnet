
from modules import Module
from modules.translator import Translator


class Notifier(Module):
    """Creates notifications to force user
    to take certain actions."""
    platforms = ["win32", "linux"]
    description = __doc__
    administrator = {"win32": False, "linux": False}

    def __init__(self):
        super(Notifier, self).__init__()

    def run(self, title, description, duration=60, icon_path=None):
        from pynotifier import Notification

        if Translator.enabled:
            translator = Translator()
            try:
                _title = translator.run(title)
                _description = translator.run(description)
                if _title and _description:
                    title = _title
                    description = _description
            except Exception:  # noqa
                pass

        Notification(
            title=title,
            description=description,
            icon_path=icon_path,
            duration=duration,
            urgency="critical"
        ).send()
