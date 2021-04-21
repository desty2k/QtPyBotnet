from tasks.__task import Task
from infos import network_interfaces


class NetworkScanner(Task):
    """Scans local network for reachable devices. Returns list of IP addresses."""
    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": False, "darwin": False}

    def __init__(self, task_id):
        super(NetworkScanner, self).__init__(task_id)
        import threading
        self._run = threading.Event()

    def run(self):
        from socket import AF_INET
        from subprocess import run
        from ipaddress import ip_address, ip_interface, AddressValueError

        targets = []
        reachable = []
        for interface, snics in network_interfaces().items():
            for snic in snics:
                if snic.family == AF_INET:
                    if not ip_address(snic.address).is_loopback:
                        try:
                            iface = ip_interface(snic.address + "/" + snic.netmask)
                            hosts = list(iface.network.hosts())
                            hosts.remove(iface.ip)
                            targets = targets + hosts
                        except (AddressValueError, ValueError):
                            pass
        self._run.set()
        for ip in targets:
            if not self._run.is_set():
                break
            resp = run(["ping", str(ip), "-n", "2", "-w", "500"], capture_output=True)
            if resp.returncode == 0:
                reachable.append(str(ip))
        return reachable

    def stop(self):
        self._run.clear()
