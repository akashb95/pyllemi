import ast
import os.path
from typing import Union

IMPORT_NODE_TYPE = Union[ast.Import, ast.ImportFrom]


def is_module(path: str) -> bool:
    return os.path.isfile(path)


def is_subpackage(path: str) -> bool:
    return os.path.isdir(path)
