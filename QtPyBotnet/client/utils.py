class OutputLogger:
    """Logging cocfiguration class"""

    def __init__(self):
        super(OutputLogger, self).__init__()
        import logging
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.NOTSET)
        self.handler = logging.StreamHandler()
        self.handler.setLevel(logging.NOTSET)
        try:
            import coloredlogs
            self.formatter = coloredlogs.ColoredFormatter(
                "%(asctime)s [%(threadName)s] [%(name)s] [%(levelname)s] %(message)s")
        except ImportError:
            self.formatter = logging.Formatter(
                "%(asctime)s [%(threadName)s] [%(name)s] [%(levelname)s] %(message)s")

        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

        notify = logging.getLogger(self.__class__.__name__)
        notify.info("Logger enabled")

    def setLevel(self, level: int):
        self.logger.setLevel(level)
        self.handler.setLevel(level)


def encrypt(message: bytes, key: bytes) -> bytes:
    from cryptography.fernet import Fernet
    return Fernet(key).encrypt(message)


def decrypt(data: bytes, key: bytes) -> bytes:
    from cryptography.fernet import Fernet
    return Fernet(key).decrypt(data)


def get_class_by_name(name: str):
    import sys
    try:
        return getattr(sys.modules[__name__], name)
    except AttributeError:
        return None


def random_string(length):
    """Creates random string."""
    import string
    import random
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_language():
    """Language used in system"""
    import locale  # noqa
    try:
        lang, _ = locale.getdefaultlocale()
        return lang.split("_")[0]
    except Exception:  # noqa
        # do not translate if error
        return None


def average(data: list):
    """Calculates the average of a list of values."""
    return sum(data)/len(data)


def dateToStr(date):
    """Convert date object to string."""
    return date.strftime("%Y-%m-%d %H:%M:%S")


def strToDate(date: str):
    from datetime import datetime
    return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")


from threading import Thread
from functools import wraps


class TaskThread(Thread):
    def __init__(self, group=None, target_func=None, name=None, args=(), kwargs=None, *, daemon=None):
        Thread.__init__(self, group, target_func, name, args, kwargs, daemon=daemon)
        self.result = None
        self.exit_code = None

    def run(self):
        if self._target is not None:
            try:
                self.result = self._target(*self._args, **self._kwargs)
                self.exit_code = 0
            except Exception as e:
                self.result = e
                self.exit_code = 1

    def join(self, timeout=None):
        Thread.join(self, timeout)
        return {"result": self.result, "exit_code": self.exit_code}


def threaded_task(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        thread = TaskThread(target_func=function, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper



import json
import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class MessageEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {
                "_type": "datetime",
                "value": obj.strftime(DATETIME_FORMAT)
            }
        return super(MessageEncoder, self).default(obj)


class MessageDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(MessageDecoder, self).__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if '_type' not in obj:
            return obj
        obj_type = obj['_type']
        if obj_type == 'datetime':
            return datetime.datetime.strptime(obj["value"], DATETIME_FORMAT)
        return obj
