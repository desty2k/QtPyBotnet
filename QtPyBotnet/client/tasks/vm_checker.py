from tasks.__task import Task


class VMChecker(Task):
    """Check if running in virtual machine or in Docker."""
    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": False, "darwin": False}
    kwargs = {"check_frequency": {"type": int,
                                  "description": "Delay between next checks in seconds.",
                                  "default": 300}}

    def __init__(self, task_id):
        super(VMChecker, self).__init__(task_id)
        import logging
        import threading

        self._logger = logging.getLogger(self.__class__.__name__)
        self._run = threading.Event()

    def run(self, **kwargs):
        from sys import exit
        from time import sleep
        from infos import is_running_in_vm, is_running_in_docker
        check_frequency = kwargs.get("check_frequency")
        self._run.set()
        while self._run.is_set():
            if is_running_in_vm() or is_running_in_docker():
                exit(0)
            sleep(check_frequency)
        return "Task stopped successfully."

    def stop(self):
        self._run.clear()
