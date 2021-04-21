import socket

from tasks.__task import Task

PORTS_FULL = [7, 9, 11, 13, 17, 19, 20, 21, 22, 23, 25, 37, 42, 43, 53, 70, 79, 80, 81, 88, 101, 102, 107, 109, 110,
              111, 113, 117, 118, 119, 135, 137, 139, 143, 150, 156, 158, 170, 179, 194, 322, 349, 389, 443, 445, 464,
              507, 512, 513, 514, 515, 520, 522, 526, 529, 530, 531, 532, 540, 543, 544, 546, 547, 548, 554, 556, 563,
              565, 568, 569, 593, 612, 613, 636, 666, 691, 749, 800, 989, 990, 992, 993, 994, 995, 1034, 1109, 1110,
              1155, 1270, 1433, 1434, 1477, 1478, 1512, 1524, 1607, 1711, 1723, 1731, 1745, 1755, 1801, 1863, 1900,
              1944, 2053, 2106, 2177, 2234, 2382, 2383, 2393, 2394, 2460, 2504, 2525, 2701, 2702, 2703, 2704, 2725,
              2869, 3020, 3074, 3126, 3132, 3268, 3269, 3306, 3343, 3389, 3535, 3540, 3544, 3587, 3702, 3776, 3847,
              3882, 3935, 4350, 4500, 5355, 5357, 5358, 5678, 5679, 5720, 6073, 7680, 9535, 9753, 11320, 47624]

PORTS_IMPORTANT = [7, 9, 11, 13, 17, 19, 20, 21, 22, 23, 25, 37, 42, 43, 53, 70, 79, 80, 81, 88, 101, 102, 107, 109,
                   110, 111, 113, 117, 118, 119, 135, 137, 139, 143, 150, 156, 158, 170, 179, 194, 322, 349, 389, 443,
                   445, 464, 507, 512, 513, 514, 515, 520, 522, 526, 529, 530, 531, 532, 540, 543, 544, 546, 547, 548,
                   554, 556, 563, 565, 568, 569, 593, 612, 613, 636, 666, 691, 749, 800, 989, 990, 992, 993, 994, 995]

PORTS_MINIMAL = [20, 21, 22, 23, 25, 53, 80, 88, 110, 119, 123, 143, 194, 443]


class PortScanner(Task):
    """Scanning opened ports."""
    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": False, "darwin": False}
    kwargs = {"ports": {"type": list, "description": "List of ports to scan", "default": PORTS_MINIMAL}}

    def __init__(self, task_id):
        super(PortScanner, self).__init__(task_id)
        import logging
        import threading

        self._logger = logging.getLogger(self.__class__.__name__)
        self._run = threading.Event()

    def run(self, **kwargs):
        assert "ports" in kwargs, "Missing keyword argument ports!"
        ports = list(kwargs.get("ports"))

        from ipaddress import ip_address
        ip = socket.gethostbyname(socket.gethostname())
        self._logger.info("Starting task {}".format(self.__class__.__name__))
        opened = []
        closed = []

        try:
            ip_address(ip)
        except ValueError as e:
            raise ValueError("IP address is invalid: {}".format(e))

        if ports is None:
            ports = PORTS_MINIMAL
        elif type(ports) is not list:
            raise ValueError("Ports argument must be list, got {}".format(type(ports)))

        self._run.set()
        for port in ports:
            try:
                port = int(port)
                if port not in range(1, 65536):
                    closed.append(port)
                    continue
            except TypeError:
                closed.append(port)
                continue
            if self._run.is_set():
                self._logger.debug("Testing port {}".format(port))
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        client.settimeout(2)
                        x = client.connect_ex((ip, port))
                        if x == 0:
                            opened.append(port)
                            self._logger.debug("Port {} is open".format(port))
                        else:
                            closed.append(port)
                            self._logger.debug("Port {} is closed".format(port))
                except Exception as e:
                    self._logger.info("Exception while connecting to port {}: {}".format(port, e))
            else:
                break
        return {"open": opened, "closed": closed}

    def stop(self):
        self._run.clear()
