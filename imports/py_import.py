import os

from dataclasses import dataclass
from enum import IntEnum, unique


@unique
class ImportType(IntEnum):
    UNKNOWN = 0
    MODULE = 1
    PACKAGE = 2


@dataclass
class Import:
    import_: str
    type_: ImportType

    def __eq__(self, other: "Import") -> bool:
        return self.import_ == other.import_ and self.type_ == other.type_


def resolve_import_type(py_import_path: str) -> ImportType:
    """
    Given a Python import path (such as `x.y.z`), determine whether the import path
    leads to a module or package, or if it is unknown (cannot be determined by
    checking the filesystem).

    If unknown, this could be because the import is:
    * Erroneous; or
    * Is a 3rd-party module import; or
    * Is a builtin module import.
    """

    filename_or_dirname = os.path.abspath(py_import_path.replace(".", os.path.sep))

    if os.path.isdir(filename_or_dirname):
        # If pkg is a directory, then return simply the Python package.
        return ImportType.PACKAGE

    # If pkg is a file, then the import path leads to a module,
    # which should be a Python file, and has a .py (or .pyi) extension.
    if os.path.isfile(f"{filename_or_dirname}.py") or os.path.isfile(f"{filename_or_dirname}.pyi"):
        return ImportType.MODULE

    return ImportType.UNKNOWN
