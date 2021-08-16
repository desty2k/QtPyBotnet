from qtpy.QtCore import Signal, Slot
from QtPyNetwork.client import QThreadedClient

import json
import logging
from cryptography.fernet import InvalidToken

from models.Device import Device
from client.utils import MessageDecoder, MessageEncoder
from core.crypto import validate_token, encrypt, decrypt


class SecureClient(QThreadedClient):
    message = Signal(dict)

    def __init__(self):
        super(SecureClient, self).__init__()
        self.server_ip = None
        self.server_port = None
        self.key = None
        self.logger = logging.getLogger(self.__class__.__name__)

    @Slot(str, int, bytes)
    def start(self, ip, port, key):
        self.key = key
        super().start(ip, port)

    @Slot(bytes)
    def on_message(self, message: bytes) -> dict:
        if self.key and validate_token(message):
            self.logger.encrypted_message("Received bytes: {}".format(message))
            message = decrypt(message, self.key)
            self.logger.message("Received decrypted: {}".format(message))
        else:
            self.decryption_error.emit(message)
        try:
            message = json.loads(message, cls=MessageDecoder)
            if message.get("event_type") == "assign":
                encryption_key = message.get("encryption_key")
                self.write({"event_type": "assign", "encryption_key": encryption_key})
                self.key = encryption_key
                self.connected.emit(self.server_ip, self.server_port)
                return {}
            else:
                self.message.emit(message)
                return message
        except json.JSONDecodeError as e:
            self.logger.error("Failed to decode message {}: {}".format(message, e))

    @Slot(str, int)
    def on_connected(self, ip, port):
        self.server_ip = ip
        self.server_port = port

    @Slot(dict)
    def write(self, message: dict):
        try:
            message = json.dumps(message, cls=MessageEncoder).encode()
            if self.key:
                message = encrypt(message, self.key)
            super().write(message)
        except (json.JSONDecodeError, InvalidToken):
            self.encryption_error.emit(Device, message)
