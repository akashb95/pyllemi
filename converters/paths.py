import os
from typing import Optional


def convert_py_import_path_to_os_path(py_import_path: str) -> Optional[str]:
    """
    `pkg.x` could be the following:

    1. pkg is a module, x is an object
    2. pkg is a directory, x is an importable file (module)
    3. pkg is a directory, x is a directory (subpackage)
    4. Path to pkg cannot be found, possibly because it is a builtin/3rd-party module (returns None).

    Provided we know x is NOT an object, x can be a .pyi? file
    """

    filename_or_dirname = os.path.abspath(py_import_path.replace(".", os.path.sep))

    if os.path.isdir(dirname := filename_or_dirname):
        # If pkg is a directory, then return simply the Python package.
        return dirname

    # If pkg is a file, then the import path leads to a module,
    # which should be a Python file, and has a .py (or .pyi) extension.
    if os.path.isfile(filename := f"{filename_or_dirname}.py"):
        return filename

    if os.path.isfile(filename := f"{filename_or_dirname}.pyi"):
        return filename


def convert_os_path_to_import_path(os_path: str, abs_path_to_project_root: str = "") -> str:
    return (
        # Discard file extensions, if any, e.g. 'py', 'pyi', etc.
        os.path.splitext(os_path)[0]
        # Path to Python module from project root.
        .removeprefix(abs_path_to_project_root)
        # Remove any leading path separators.
        .lstrip(os.path.sep)
        # Turn OS path to Python path.
        .replace(os.path.sep, ".")
    )
