import logging
import coloredlogs


class Logger:
    def __init__(self):
        super(Logger, self).__init__()
        self.logger = None
        self.handler = None
        self.formatter = None

    def enable(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.NOTSET)

        self.handler = logging.StreamHandler()
        self.handler.setLevel(logging.NOTSET)

        self.formatter = coloredlogs.ColoredFormatter("%(asctime)s "
                                                      "[%(threadName)s] "
                                                      "[%(name)s] "
                                                      "[%(levelname)s] "
                                                      "%(message)s")
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        self.logger.info("Logger enabled")
        return self.logger

    def set_level(self, level):
        if self.logger and self.handler:
            self.logger.setLevel(level)
            self.handler.setLevel(level)
        else:
            raise Exception("Logger not enabled!")
