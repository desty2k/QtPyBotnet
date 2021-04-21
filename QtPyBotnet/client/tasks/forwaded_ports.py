import socket

from tasks.__task import Task
from tasks.upnp import UPnPForward
from utils import random_string, threaded
from infos import public_ip


PORTS = [20, 21, 22, 23, 25, 53, 80, 88, 110, 119, 123, 143, 194, 443]


class ForwadedPorts(Task):
    """Checking forwaded ports."""
    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": False, "darwin": False}
    kwargs = {"use_upnp": {"type": bool, "description": "Try to create forwading rules using UPnP", "default": True},
              "return_first_found": {"type": bool, "description": "Return first found port", "default": False}}

    def __init__(self, task_id):
        super(ForwadedPorts, self).__init__(task_id)
        import logging
        import threading

        self._logger = logging.getLogger(self.__class__.__name__)
        self._run = threading.Event()

    # def run(self, use_upnp=True, find_first=False):
    def run(self, **kwargs):
        assert "use_upnp" in kwargs, "Missing keyword argument use_upnp!"
        assert "return_first_found" in kwargs, "Missing keyword argument return_first_found!"

        use_upnp = bool(kwargs.get("use_upnp"))
        return_first_found = bool(kwargs.get("return_first_found"))

        self._logger.debug("Getting public IP address...")
        try:
            target_ip = public_ip()
        except Exception as e:
            raise Exception("Failed to obtain public IP address: {}".format(e))
        local_ip = socket.gethostbyname(socket.gethostname())
        self._logger.debug("Public IP is {}".format(target_ip))
        self._logger.debug("Private IP is {}".format(local_ip))
        self._run.set()

        results = {"closed": [], "open": [], "ip": local_ip, "public_ip": target_ip}

        for port in PORTS:
            if self._run.is_set():
                try:
                    if use_upnp:
                        self._logger.debug("Testing port {}".format(port))
                        srv = self._setup_server(local_ip, port)
                        cln = self._setup_client(target_ip, port)
                        srv.join()
                        resp = cln.join()
                        result = resp.get("result")

                        if int(resp.get("exit_code")) != 0:
                            raise Exception(result)

                        if result is not None:
                            results["open"].append(port)
                            if return_first_found:
                                return results
                            continue
                        else:
                            open_port = UPnPForward(0)
                            open_port.set_thread(open_port.start(internal_port=port,
                                                                 external_port=port,
                                                                 internal_ip=local_ip))
                            open_port.join()

                    self._logger.debug("Testing port {}".format(port))
                    srv = self._setup_server(local_ip, port)
                    cln = self._setup_client(target_ip, port)
                    srv.join()
                    resp = cln.join()
                    result = resp.get("result")

                    if int(resp.get("exit_code")) != 0:
                        raise Exception(result)

                    if result is not None:
                        results["open"].append(port)
                    else:
                        results["closed"].append(port)

                except Exception as e:
                    self._logger.error("Error while checking port {}: {}".format(port, e))
                    results["closed"].append(port)
            else:
                return results
        return results

    def stop(self):
        self._run.clear()

    @threaded
    def _setup_server(self, ip, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((ip, port))
            server.listen()
            server.settimeout(2)
            conn, addr = server.accept()
            with conn:
                data = conn.recv(256)
                conn.sendall(data)

    @threaded
    def _setup_client(self, ip, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client.settimeout(2)
            x = client.connect_ex((ip, port))
            if x == 0:
                send = random_string(30).encode()
                client.sendall(send)
                resp = client.recv(256)
                self._logger.debug("Port {}: Sent: {} Received: {}".format(port, send, resp))
                if send == resp:
                    self._logger.debug("Found forwared port {}".format(port))
                    return port
                else:
                    self._logger.debug("Connected to port {}, but sent string and response vary ({}/{})".format(port,
                                                                                                                send,
                                                                                                                resp))
                    return None
            else:
                self._logger.debug("Port {} not forwaded".format(port))
                return None
