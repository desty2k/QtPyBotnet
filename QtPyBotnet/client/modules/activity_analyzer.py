from modules import Module


class ActivityAnalyzer(Module):
    """Analyzes user activity and executes tasks in appropriate time."""
    platforms = ["win32", "darwin", "linux"]
    description = __doc__
    administrator = {"win32": False, "darwin": False, "linux": False}

    def __init__(self):
        super(ActivityAnalyzer, self).__init__()

    def run(self):
        import psutil

        if self.enabled:
            cpu = psutil.cpu_percent() * 8
            ram = psutil.virtual_memory().percent * 2

            # net_old = 0
            # net_new = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
            # net = net_new - net_old
            # net_old = net_new

            lvl = float(cpu+ram)/100

            if lvl >= 9.5:  # Very high
                return 5
            elif 9.5 > lvl >= 7.5:  # High
                return 4
            elif 7.5 > lvl >= 5.0:  # Medium
                return 3
            elif 5 > lvl >= 2:  # Normal
                return 2
            elif 2 > lvl > 0:  # Low
                return 1
            else:  # Not supported
                return 0
