import os
from glob import glob
from typing import Optional

from common.logger.logger import setup_logger
from domain.python_import import enriched as enriched_import

LOGGER = setup_logger(__name__)


def resolve_import_type(py_import_path: str, python_moduledir: str) -> enriched_import.Type:
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
        return enriched_import.Type.THIRD_PARTY_MODULE

    abs_filepath_without_ext_or_dirpath = os.path.abspath(py_import_path.replace(".", os.path.sep))

    if os.path.isdir(abs_filepath_without_ext_or_dirpath):
        return enriched_import.Type.PACKAGE

    # If path is a file, then the import path leads to a module,
    # which should be a Python file, and has a .py (or .pyi) extension.
    abs_filepath_without_ext = abs_filepath_without_ext_or_dirpath
    if os.path.isfile(f"{abs_filepath_without_ext}.py"):
        return enriched_import.Type.MODULE
    if os.path.isfile(f"{abs_filepath_without_ext}.pyi"):
        return enriched_import.Type.STUB

    # Finally, check if the import can be of a protobuf-generated file.
    # In Python, all protobuf generated files must be of the form *_pb2.py or *_pb2_grpc.py
    if abs_filepath_without_ext.endswith("_pb2") or abs_filepath_without_ext.endswith("_pb2_grpc"):
        candidate_abs_proto_filepath = (
            f"{abs_filepath_without_ext.removesuffix('_pb2').removesuffix('_pb2_grpc')}.proto"
        )
        if os.path.isfile(candidate_abs_proto_filepath):
            return enriched_import.Type.PROTOBUF_GEN

    return enriched_import.Type.UNKNOWN


def to_whatinputs_input(import_: enriched_import.Import) -> Optional[list[str]]:
    """
    Output depends on the Import's Type.
    """

    os_path_from_reporoot = import_.import_.replace(".", os.path.sep)
    if import_.type_ == enriched_import.Type.MODULE:
        return [os_path_from_reporoot + ".py"]
    if import_.type_ == enriched_import.Type.STUB:
        return [os_path_from_reporoot + ".pyi"]
    if import_.type_ == enriched_import.Type.PROTOBUF_GEN:
        return [os_path_from_reporoot.removesuffix("_pb2").removesuffix("_pb2_grpc") + ".proto"]

    if import_.type_ == enriched_import.Type.PACKAGE:
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
