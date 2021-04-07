
from modules import Module
from utils import get_language


class Translator(Module):
    """Translate strings"""
    platforms = ["win32", "darwin", "linux"]
    description = __doc__
    administrator = {"win32": False, "darwin": False, "linux": False}

    def __init__(self):
        super(Translator, self).__init__()

    def run(self, text, to_lang=get_language()):
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source='auto', target=to_lang).translate(text)
