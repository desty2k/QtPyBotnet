import sys
import pydoc
import inspect
import pkgutil
import pathlib
import importlib
import importlib.util


def class_importer(path, target_type, import_private=False):
    """Searches for object of target_type type in path.
    Imports them and returns list of objects."""

    package_dir = str(pathlib.Path(path).resolve())
    sys.path.append(package_dir)
    objs = []

    for (_, module_name, _) in pkgutil.iter_modules([package_dir]):
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # skip imported objects
            if obj.__module__ == module.__name__:
                # skip objects which type is target type but are not subclassing it
                if obj is not target_type and issubclass(obj, target_type):
                    # do not import private classes
                    if import_private:
                        objs.append(obj)
                    else:
                        if not obj.__name__.startswith("_"):
                            objs.append(obj)

    sys.path.remove(package_dir)
    return objs


def get_subclassess_by_name(path, target_class, import_private=False):
    """Searches for object of target_type type in path.
    Imports them and returns list of objects."""
    target_class = pydoc.locate(target_class)

    package_dir = str(pathlib.Path(path).absolute())
    sys.path.append(package_dir)
    objs = []

    for (_, module_name, _) in pkgutil.iter_modules([package_dir]):
        if module_name != target_class.__name__:
            module = importlib.import_module(module_name)
            for cls in dir(module):  # <-- Loop over all objects in the module's namespace
                cls = getattr(module, cls)
                if (inspect.isclass(cls)  # Make sure it is a class
                        and inspect.getmodule(cls) == module  # Make sure it was defined in module, not just imported
                        and issubclass(cls, target_class)):  # Make sure it is a subclass of base
                    # do not import private classes
                    if import_private:
                        objs.append(cls)
                    else:
                        if not cls.__name__.startswith("_"):
                            objs.append(cls)

    sys.path.remove(package_dir)
    return objs


def function_importer(script_path, script_name):
    """Returns list of functions in script."""
    package_dir = str(pathlib.Path(script_path).absolute())
    sys.path.append(package_dir)
    infos = importlib.import_module(script_name)
    members = inspect.getmembers(infos, inspect.isfunction)
    sys.path.remove(package_dir)
    return [fun[0] for fun in members]
