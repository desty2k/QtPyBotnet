FROM python:3.9
WORKDIR .
COPY requirements.txt .

RUN \
    set -e \
    && apt update \
    && apt install libsm6 libgl1-mesa-glx python3-pyqt5.qtwebengine python3-pyqt5.qtmultimedia -y \
    && pip install -r requirements.txt

COPY QtPyBotnet/ .
CMD ["python", "server.py", "--nogui"]
