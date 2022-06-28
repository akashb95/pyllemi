import os
from dataclasses import dataclass
from enum import IntEnum, unique
from glob import glob
from typing import Optional

from common.logger.logger import setup_logger

LOGGER = setup_logger(__name__)


@unique
class ImportType(IntEnum):
    UNKNOWN = 0
    MODULE = 1
    PACKAGE = 2
    STUB = 3
    THIRD_PARTY_MODULE = 4
    PROTOBUF_GEN = 5


@dataclass
class EnrichedImport:
    import_: str
    type_: ImportType

    def __eq__(self, other: "EnrichedImport") -> bool:
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

    abs_filepath_without_ext_or_dirpath = os.path.abspath(py_import_path.replace(".", os.path.sep))

    if os.path.isdir(abs_filepath_without_ext_or_dirpath):
        return ImportType.PACKAGE

    # If path is a file, then the import path leads to a module,
    # which should be a Python file, and has a .py (or .pyi) extension.
    abs_filepath_without_ext = abs_filepath_without_ext_or_dirpath
    if os.path.isfile(f"{abs_filepath_without_ext}.py"):
        return ImportType.MODULE
    if os.path.isfile(f"{abs_filepath_without_ext}.pyi"):
        return ImportType.STUB

    # Finally, check if the import can be of a protobuf-generated file.
    # In Python, all protobuf generated files must be of the form *_pb2.py or *_pb2_grpc.py
    if (abs_filepath_without_ext.endswith("_pb2") or abs_filepath_without_ext.endswith("pb2_grpc")) and os.path.isfile(
        f"{abs_filepath_without_ext}.proto"
    ):
        return ImportType.PROTOBUF_GEN

    return ImportType.UNKNOWN


def to_whatinputs_input(import_: EnrichedImport) -> Optional[list[str]]:
    """
    Output depends on the EnrichedImport type.

    For ImportType.MODULE, the output is a `.py` file.
    For ImportType.PACKAGE, the output is a glob matching `**/*.py` under the given (Python) package.
    For anything else, return None.
    """

    os_path_from_reporoot = import_.import_.replace(".", os.path.sep)
    if import_.type_ == ImportType.MODULE:
        return [os_path_from_reporoot + ".py"]
    if import_.type_ == ImportType.STUB:
        return [os_path_from_reporoot + ".pyi"]
    if import_.type_ == ImportType.PROTOBUF_GEN:
        return [os_path_from_reporoot + ".proto"]

    if import_.type_ == ImportType.PACKAGE:
        all_paths: list[str] = [
            *glob(os.path.join(os_path_from_reporoot, "**", "*.py"), recursive=True),
            *glob(os.path.join(os_path_from_reporoot, "**", "*.pyi"), recursive=True),
            *glob(os.path.join(os_path_from_reporoot, "**", "*.proto"), recursive=True),
        ]

        if not all_paths:
            LOGGER.warning(f"Could not find any importable modules in package '{import_.import_}'.")
            return None
        return all_paths
    return None
