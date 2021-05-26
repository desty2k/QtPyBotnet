import os
import shlex
import shutil
import pathlib
import subprocess


class Shell:
    def __init__(self):
        super(Shell, self).__init__()

    def ls(self, path="."):
        """Show directory contents"""
        return "\n".join(os.listdir(path))

    def dir(self, path="."):
        """Show directory contents"""
        return self.ls(path)

    def cp(self, src, dest):
        """Copy file"""
        return shutil.copy(src, dest)

    def cp2(self, src, dest):
        """Copy file and metadata"""
        return shutil.copy2(src, dest)

    def cptree(self, src, dest):
        """Copy directory tree"""
        return shutil.copytree(src, dest)

    def mv(self, srv, dest):
        """Move file"""
        shutil.move(srv, dest)

    def sh(self, command):
        """Run sh command"""
        return subprocess.check_output(shlex.split(command), creationflags=subprocess.CREATE_NO_WINDOW,
                                       shell=True, text=True)

    def touch(self, name):
        """Create file"""
        mfile = pathlib.Path(name)
        mfile.touch(exist_ok=True)
        return str(mfile.resolve())

    def mkdir(self, path):
        """Create directory tree"""
        mdir = pathlib.Path(path)
        mdir.mkdir(parents=True, exist_ok=True)
        return str(mdir.resolve())

    def cd(self, path):
        """Change working dir"""
        os.chdir(path)
        return self.cwd()

    def help(self, name=""):
        """Show help"""
        if name:
            return str(name) + "    " + getattr(self, str(name)).__doc__
        else:
            output = ""
            for m in [m for m in dir(self) if not m.startswith("_")]:
                output = output + str(m) + "    " + getattr(self, m).__doc__ + "\n"
            return output

    def cat(self, path):
        """Show file contents"""
        with open(path, "r") as f:
            return f.read()

    def rm(self, name):
        """Remove file"""
        return os.remove(name)

    def rmdir(self, path):
        """Remove directory tree"""
        return shutil.rmtree(path)

    def eval(self, code):
        """Evaluate Python code"""
        return eval(code)

    def exec(self, code):
        """Execute Python code"""
        return exec(code)

    def wget(self, url, filename=None):
        """Download website or file"""
        if not url.startswith("http"):
            raise Exception("Url string must begin with http!")
        from urllib.request import urlretrieve
        path, _ = urlretrieve(url, filename) if filename else urlretrieve(url)
        return path

    def cwd(self):
        """Get current dir"""
        return os.getcwd()

    def pwd(self):
        """Get current dir"""
        return os.getcwd()
