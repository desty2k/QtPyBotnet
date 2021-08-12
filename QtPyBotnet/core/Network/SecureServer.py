from qtpy.QtCore import Signal, Slot
from QtPyNetwork.server import QBalancedServer, QThreadedServer
from QtPyNetwork.server.BaseServer import QBaseServer

import json
import logging
from cryptography.fernet import InvalidToken

from models.Device import Device
from client.utils import MessageDecoder, MessageEncoder
from core.crypto import encrypt, decrypt, validate_token, generate_key


class SecureServer(QBaseServer):
    encryption_error = Signal(Device, bytes)
    decryption_error = Signal(Device, bytes)
    message = Signal(Device, dict)

    def __init__(self, require_verification=True):
        super(SecureServer, self).__init__(None)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.key = None
        self.require_verification = require_verification

    @Slot(str, int, bytes)
    def start(self, ip, port, key):
        self.key = key
        super().start(ip, port)

    @Slot(Device, str, int)
    def on_connected(self, device: Device, ip, port):
        device.key = self.key
        if self.require_verification:
            device.custom_key = generate_key()
            device.write({"event_type": "assign", "encryption_key": device.custom_key.decode()})
        else:
            device.set_verified(True)
            self.connected.emit(device, ip, port)

    @Slot(Device, bytes)
    def on_message(self, device: Device, message: bytes) -> dict:
        if validate_token(message):
            message = decrypt(message, device.key)
            try:
                message = json.loads(message, cls=MessageDecoder)
            except json.JSONDecodeError as e:
                self.logger.error("Failed to decode message {}: {}".format(message, e))
                raise Exception("Failed to decode message")

            if device.is_verified():
                self.message.emit(device, message)
                return message
            else:
                if message.get("event_type") == "assign":
                    if str(message.get("encryption_key")).encode() == device.custom_key:
                        device.key = device.custom_key
                        self.connected.emit(device, device.ip(), device.port())
                    else:
                        self.logger.warning("Assigned keys do not match! Bot {} will be kicked!".format(device.id()))
                        device.kick()
                return message
        else:
            self.decryption_error.emit(device, message)
            raise Exception("Message is not valid")

    @Slot(Device, dict)
    def write(self, device: Device, message: dict):
        try:
            if device.is_verified():
                message = json.dumps(message, cls=MessageEncoder).encode()
                message = encrypt(message, device.key)
                super().write(device, message)
        except (json.JSONDecodeError, InvalidToken):
            self.encryption_error.emit(Device, message)

    @Slot(dict)
    def write_all(self, message: dict):
        message = json.dumps(message, cls=MessageEncoder).encode()
        for device in self.get_devices():
            if device.is_verified():
                try:
                    encrypted = encrypt(message, device.key)
                    super().write(device, encrypted)
                except (json.JSONDecodeError, InvalidToken):
                    self.encryption_error.emit(device, message)


class SecureThreadedServer(SecureServer, QThreadedServer):

    def __init__(self, require_verification):
        super(SecureThreadedServer, self).__init__(require_verification)


class SecureBalancedServer(SecureServer, QBalancedServer):

    def __init__(self):
        super(SecureBalancedServer, self).__init__()
