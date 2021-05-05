QtPyBotnet
==========

C2 Server
---------

- [x] GUI built with Qt for Python
- [x] Frameless windows design using qrainbowstyle
- [x] Multithreaded C2 and GUI servers using QtPyNetwork
- [x] Google Maps widget with connected bots and their location
- [x] After setup can be controlled from remote GUI (remote first configuration in TODO)
- [ ] Clustering support

Client
------

- [x] Multithreaded network IO
- [x] Encrypted socket connection
- [x] Encryption key negotiating after successfull connection
- [x] Single executable built with Pyinstaller
- [x] Cross platform payload generator (win32, win64, i386, amd64)
- [x] Encrypted code using PyArmor


Tasks
~~~~~
- [x] VM checker - terminates app if running in virtual machine or in Docker.
- [x] Translator - translates text in notifications and emails with system language.
- [x] User activity analyzer - calculates user activity factor from CPU / RAM load and executes tasks in right time.
- [x] Notifier - can create custom notifications to force user to take certain actions.
- [x] Relay - Searches for forwaded ports and tries to create UPnP rules. Listens for new connections from other clients and forwards them to C2 servers. Does not decrypt forwaded data.
- [x] Clipboard logger - periodically dumps clipboard contents.
- [x] Clipboard replacer - replaces clipboard contents which matches regex e.g Bitcoin addresses.
- [x] Cloud drives spreaders - replicate to cloud drives. Currently OneDrive only.
- [x] Crasher - tries to crash OS using various methods.
- [x] Forwaded ports - scans for forwaded ports.
- [x] Input block - blocks mouse and keyboard. Kills task manager if opened.
- [x] Keylogger - logs clicked keys.
- [x] Persistence - tries to add trojan to startup.
- [x] Port scanner - scans for opened port (may not be forwaded).
- [x] Powershell - execute Powershell commands.
- [x] Python exec - execute Python code inside interpreter.
- [x] Screenshot - takes screenshost of all available displays.
- [x] System credentials stealer - uses social engineering to steal device owner password.
- [x] UPnP - tries to create UPnP port forwading rules on routers.
- [x] Network scanner
- [ ] SSH spreader
- [ ] WinRM spreader
- [ ] E-mail spreader
- [ ] Google Drive/Dropbox spreader
- [ ] Cookie stealer
- [ ] DDoS
- [/] Webcam
- [ ] Remote desktop
- [ ] OS destroyer

Preview images
--------------

.. image:: https://raw.githubusercontent.com/desty2k/QtPyBotnet/master/images/preview-img-1.jpg

.. image:: https://raw.githubusercontent.com/desty2k/QtPyBotnet/master/images/preview-img-2.jpg

.. image:: https://raw.githubusercontent.com/desty2k/QtPyBotnet/master/images/preview-img-3.jpg

.. image:: https://raw.githubusercontent.com/desty2k/QtPyBotnet/master/images/preview-img-4.jpg


Installation
------------

1. Download QtPyNetwork from https://github.com/desty2k/QtPyNetwork and install it using

    .. code:: bash

        pip install .


2. Clone QtPyBotnet repository
3. Install requirements using

    .. code:: bash

        pip install -r requirements.txt

4. Open terminal and run

    .. code:: bash

        python server.py

5. Follow first setup wizard.

If you want to reset configuration use

    .. code:: bash

        python server.py --reset
