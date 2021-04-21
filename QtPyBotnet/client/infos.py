def geolocation():
    """Get device location"""
    import json
    from urllib.request import urlopen
    response = urlopen('http://ipinfo.io').read()
    json_data = json.loads(response)
    latitude, longitude = json_data.get('loc').split(',')
    return latitude, longitude


def language():
    """Language used in system"""
    import locale
    try:
        lang, _ = locale.getdefaultlocale()
        return lang.split("_")[0]
    except Exception:  # noqa
        # do not translate if error
        return None


def platform():
    """Return the system platform of host machine"""
    import sys
    return sys.platform


def public_ip():
    """Return public IP address of host machine"""
    from urllib.request import urlopen
    return urlopen('http://api.ipify.org').read().decode()


def architecture():
    """Check if host machine has 32-bit or 64-bit processor architecture"""
    import struct
    return int(struct.calcsize('P') * 8)


def system_architecture():
    """Check if host machine has 32-bit or 64-bit system installed"""
    import platform
    return int(platform.architecture()[0].replace("bit", ""))


def administrator():
    """True if current user is administrator, otherwise False"""
    import os
    import ctypes
    return bool(ctypes.windll.shell32.IsUserAnAdmin() if os.name == 'nt' else os.getuid() == 0)


def username():
    """Returns current user name."""
    import getpass
    return getpass.getuser()


def is_running_in_docker():
    from os import path
    if platform() != "linux":
        return False

    if path.exists('/.dockerenv'):
        return True
    else:
        return False


def network_interfaces():
    from psutil import net_if_addrs
    return net_if_addrs()


def is_running_in_vm():
    from subprocess import run, CREATE_NO_WINDOW
    vm_services = ['xenservice', 'vboxservice', 'vboxtray', 'vmusrvc', 'vmsrvc',
                   'vmwareuser', 'vmwaretray', 'vmtoolsd', 'vmcompute', 'vmmem']
    linux_manufacturers = ['VMware, Inc.', 'Xen', 'KVM', 'VirtualBox']
    darwin_manufacturers = ['VirtualBox', 'Oracle', 'VMware', 'Parallels']

    os = platform()
    if os == "win32":
        tasks = run(["tasklist"], shell=True, capture_output=True, creationflags=CREATE_NO_WINDOW)
        if tasks.returncode:
            raise Exception("Failed to execute tasklist command! Can not check if running on virtual machine!")
        else:
            if any(service.encode() in tasks.stdout for service in vm_services):
                return True

    elif os == "linux":
        manufacturer = run(["dmidecode", "-s", "system-manufacturer"], shell=True,
                           capture_output=True, creationflags=CREATE_NO_WINDOW)
        if manufacturer.returncode:
            raise Exception("Failed to execute dmidecode command! Can not check if running on virtual machine!")
        else:
            if any(man.encode() in manufacturer.stdout for man in linux_manufacturers):
                return True

    elif os == "darwin":
        manufacturer = run(["ioreg", "-l", "|", "grep", "-e", "Manufacturer", "-e", "'Vendor Name'"], shell=True,
                           capture_output=True, creationflags=CREATE_NO_WINDOW)
        if manufacturer.returncode:
            raise Exception("Failed to execute ioreg command! Can not check if running on virtual machine!")
        else:
            if any(man.encode() in manufacturer.stdout for man in darwin_manufacturers):
                return True

    else:
        raise OSError("OS not supported.")

    return False
