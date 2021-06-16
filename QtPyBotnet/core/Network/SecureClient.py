from qtpy.QtCore import Signal, Slot
from QtPyNetwork.client import QThreadedClient

import json
from cryptography.fernet import InvalidToken

from models.Device import Device
from utils import MessageDecoder, MessageEncoder
from core.crypto import validate_token, encrypt, decrypt


class SecureClient(QThreadedClient):
    message = Signal(dict)

    def __init__(self):
        super(SecureClient, self).__init__(None)
        self.key = None

    @Slot(str, int, bytes)
    def start(self, ip, port, key):
        self.key = key
        super().start(ip, port)

    @Slot(bytes)
    def on_message(self, message: bytes) -> dict:
        if self.key and validate_token(message):
            message = decrypt(message, self.key)
        else:
            self.decryption_error.emit(message)

        try:
            message = json.loads(message, cls=MessageDecoder)
            self.message.emit(message)
            return message
        except json.JSONDecodeError as e:
            self.logger.error("Failed to decode message {}: {}".format(message, e))
            return

    @Slot(dict)
    def write(self, message: dict):
        try:
            message = json.dumps(message, cls=MessageEncoder).encode()
            if self.key:
                message = encrypt(message, self.key)
            super().write(message)
        except (json.JSONDecodeError, InvalidToken):
            self.encryption_error.emit(Device, message)



