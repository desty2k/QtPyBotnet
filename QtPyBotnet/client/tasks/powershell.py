from tasks.__task import Task


class Powershell(Task):
    """Execute Powershell commands."""
    platforms = ["win32"]
    description = __doc__
    administrator = {"win32": False}
    kwargs = {"command": {"type": str, "description": "Command to execute in Powershell.", "default": ""}}

    def __init__(self, task_id):
        super(Powershell, self).__init__(task_id)

    def run(self, **kwargs):
        assert "command" in kwargs, "Missing keyword argument command!"
        command = str(kwargs.get("command"))

        from subprocess import run
        return run(["powershell", "-Command", command], capture_output=True)
