from tasks.__task import Task
from utils import threaded_task


class Powershell(Task):
    """Execute Powershell commands."""
    platforms = ["win32"]
    description = __doc__
    administrator = {"win32": False}
    kwargs = {"command": {"type": str, "description": "Command to execute in Powershell.", "default": ""}}

    def __init__(self, task_id):
        super(Powershell, self).__init__(task_id)

    @threaded_task
    def start(self, command=""):
        import subprocess
        return subprocess.run(["powershell", "-Command", command], capture_output=True)
