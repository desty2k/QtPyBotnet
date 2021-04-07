from tasks.__task import Task
from utils import threaded_task

from socket import gethostname, gethostbyname


class UPnPForward(Task):
    """Tries to forward ports."""
    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": False, "darwin": False}
    experimental = False

    def __init__(self, task_id):
        super(UPnPForward, self).__init__(task_id)
        import logging
        import threading

        self._logger = logging.getLogger(self.__class__.__name__)
        self._run = threading.Event()

    @threaded_task
    def start(self, internal_port=8192, external_port=8192,
              duration=0, protocol="TCP", name="Internet access", enabled="1",
              internal_ip=gethostbyname(gethostname())):
        from ipaddress import ip_address
        try:
            addr = ip_address(internal_ip)
            if addr.is_loopback:
                raise ValueError("Address can not be loopback!")

        except ValueError as e:
            raise ValueError("Internal IP address is invalid: {}".format(e))

        import upnpclient
        devices = upnpclient.discover()
        success = 0

        for x in devices:
            if self._run.is_set():
                try:
                    x.WANIPConn1.AddPortMapping(
                        NewRemoteHost="0.0.0.0",
                        NewExternalPort=external_port,
                        NewProtocol=protocol,
                        NewInternalPort=internal_port,
                        NewInternalClient=internal_ip,
                        NewEnabled=enabled,
                        NewPortMappingDescription=name,
                        NewLeaseDuration=duration)
                    success = success + 1
                except Exception:  # noqa
                    pass
            else:
                break
        return success > 0

    def stop(self):
        self._run.clear()
