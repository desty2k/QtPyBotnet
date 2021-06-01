from tasks.__task import Task
from tasks.translator import Translator


class Notifier(Task):
    """Creates notifications to force user to take certain actions."""
    platforms = ["win32", "linux"]
    description = __doc__
    administrator = {"win32": False, "linux": False}
    kwargs = {"title": {"type": str, "description": "Notification title.", "default": ""},
              "description": {"type": str, "description": "Notification description.", "default": ""},
              "duration": {"type": int, "description": "Notification duration.", "default": 60},
              "translate": {"type": bool,
                            "description": "Use Translator task to translate notification title and description.",
                            "default": True}}
    packages = ["pynotifier"]

    def __init__(self, task_id):
        super(Notifier, self).__init__(task_id)

    def run(self, **kwargs):
        from pynotifier import Notification

        title = kwargs.get("title")
        description = kwargs.get("description")
        duration = kwargs.get("duration")
        translate = kwargs.get("translate")

        if translate:
            translator = Translator(0)
            try:
                _title = translator.start({"text": title, "to_lang": ""}).join(30).get("result")
                _description = translator.start({"text": description, "to_lang": ""}).join(30).get("result")
                if type(_title) is str and type(_description) is str:
                    title = _title
                    description = _description
                else:
                    del _title
                    del _description
            except Exception:  # noqa
                pass

        Notification(
            title=title,
            description=description,
            icon_path=None,
            duration=duration,
            urgency="critical"
        ).send()
