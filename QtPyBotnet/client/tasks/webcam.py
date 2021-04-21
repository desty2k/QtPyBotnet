from tasks.__task import Task


def cv_size(image):
    return image.shape[1], image.shape[0]


class Webcam(Task):
    """Capture image from webcam."""
    platforms = ["win32", "linux", "darwin"]
    description = __doc__
    administrator = {"win32": False, "linux": False, "darwin": False}
    experimental = True

    def __init__(self, task_id):
        super(Webcam, self).__init__(task_id)

    def run(self):
        from cv2 import VideoCapture, imencode, CAP_DSHOW
        from time import sleep
        from base64 import b64encode

        dev = VideoCapture(0, CAP_DSHOW)
        r, f = dev.read()
        sleep(1)
        dev.release()
        if not r:
            raise Exception("Unable to access webcam")

        is_success, im_buf_arr = imencode(".png", cv_size(f))
        byte_im = im_buf_arr.tobytes()
        img = b64encode(byte_im).decode()
        return {"type": "images", "images": [img]}
