from tasks.__task import Task
from utils import threaded_task


class PythonExec(Task):
    """Execute Pytohn code inside Python interpeter."""

    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": False, "darwin": False}
    kwargs = {"command": {"type": str, "description": "Command to execute in Python interpreter.", "default": ""}}

    def __init__(self, task_id):
        super(PythonExec, self).__init__(task_id)

    @threaded_task
    def start(self, command=""):
        return exec(command)
