import os
from typing import Optional

from dataclasses import dataclass
from enum import IntEnum, unique


@unique
class ImportType(IntEnum):
    UNKNOWN = 0
    MODULE = 1
    PACKAGE = 2
    STUB = 3
    THIRD_PARTY_MODULE = 4


@dataclass
class Import:
    import_: str
    type_: ImportType

    def __eq__(self, other: "Import") -> bool:
        return self.import_ == other.import_ and self.type_ == other.type_


def resolve_import_type(py_import_path: str, python_moduledir: str) -> ImportType:
    """
    Given a Python import path (such as `x.y.z`), determine whether the import path
    leads to a module, or package, or a third party module, or if it is unknown (cannot be determined by
    checking the filesystem).

    If unknown, this could be because the import is:
    * Erroneous; or
    * Is a 3rd-party module import; or
    * Is a builtin module import.
    """

    # Check if import path leads to Python moduledir as defined in Please config.
    if py_import_path.removeprefix(python_moduledir) != py_import_path:
        return ImportType.THIRD_PARTY_MODULE

    filename_or_dirname = os.path.abspath(py_import_path.replace(".", os.path.sep))

    if os.path.isdir(filename_or_dirname):
        # If pkg is a directory, then return simply the Python package.
        return ImportType.PACKAGE

    # If pkg is a file, then the import path leads to a module,
    # which should be a Python file, and has a .py (or .pyi) extension.
    if os.path.isfile(f"{filename_or_dirname}.py") or os.path.isfile(f"{filename_or_dirname}.pyi"):
        return ImportType.MODULE

    return ImportType.UNKNOWN


def to_whatinputs_input(import_: Import) -> Optional[list[str]]:
    """
    Output depends on the Import type.

    For ImportType.MODULE, the output is a `.py` file.
    For ImportType.PACKAGE, the output is a glob matching `**/*.py` under the given (Python) package.
    For anything else, return None.
    """

    os_path_from_reporoot = import_.import_.replace(".", os.path.sep)
    if import_.type_ == ImportType.MODULE:
        return [os_path_from_reporoot + ".py"]
    if import_.type_ == ImportType.STUB:
        return [os_path_from_reporoot + ".pyi"]

    if import_.type_ == ImportType.PACKAGE:
        return [
            os.path.join(os_path_from_reporoot, "**", "*.py"),
            os.path.join(os_path_from_reporoot, "**", "*.pyi"),
        ]

    return None
