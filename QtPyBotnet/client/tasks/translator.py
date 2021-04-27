from tasks.__task import Task
from utils import get_language


class Translator(Task):
    """Translate strings"""
    platforms = ["win32", "darwin", "linux"]
    description = __doc__
    administrator = {"win32": False, "darwin": False, "linux": False}
    kwargs = {"text": {"type": str, "description": "Text to translate.", "default": ""},
              "to_lang": {"type": str, "description": "Language to translate text to. If empty, use OS language.",
                          "default": ""}}

    def __init__(self, task_id):
        super(Translator, self).__init__(task_id)

    def run(self, **kwargs):
        text = str(kwargs.get("text"))
        to_lang = str(kwargs.get("to_lang"))

        if not to_lang:
            to_lang = get_language()

        from deep_translator import GoogleTranslator
        return GoogleTranslator(source='auto', target=to_lang).translate(text)
