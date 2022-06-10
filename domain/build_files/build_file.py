import ast
import logging
from typing import Optional, Union

from common.logger.logger import setup_logger
from domain.targets import target


class BUILDFile:
    def __init__(self, ast_repr: ast.Module):
        self._logger = setup_logger(__file__, logging.INFO)
        self._ast_repr: ast.Module = ast_repr
        self._ast_calls: list[ast.Call] = []  # store references to build rule definition calls for easy modification
        return

    def extract_targets(self):
        # TODO
        return

    def add_target(self, target_to_add: target.Target):
        self._ast_repr.body.append(ast.Expr(value=convert_target_to_ast_call(target_to_add)))
        return

    def update_target_attribute(self, idx: int, key: str, value: Union[list, str, int, bool]):
        # TODO
        if idx > len(self._ast_calls) - 1 or idx < 0:
            raise IndexError()
        if key not in target.Target.modifiable_attributes:
            self._logger.error(f"Programming error: not allowed to modify attribute {key}.")
        # self._ast_calls[idx] = convert_target_to_ast_call(target_to_update_to)
        return

    def dump_ast(self) -> str:
        self._logger.info(ast.unparse(self._ast_repr))

        unparsed_ast = ast.unparse(self._ast_repr)
        return unparsed_ast


def convert_target_to_ast_call(t: target.Target) -> Optional[ast.Call]:
    if t.type_ == target.PythonTargetTypes.PYTHON_LIBRARY:
        return ast.Call(
            func=ast.Name(id=target.PythonTargetTypes.PYTHON_LIBRARY.value),
            keywords=convert_kwargs_to_ast_keywords(**t.kwargs),
            args=[],
        )

    if t.type_ == target.PythonTargetTypes.PYTHON_TEST:
        return ast.Call(
            func=ast.Name(id=target.PythonTargetTypes.PYTHON_TEST.value),
            keywords=convert_kwargs_to_ast_keywords(**t.kwargs),
            args=[],
        )

    if t.type_ == target.PythonTargetTypes.PYTHON_BINARY:
        return ast.Call(
            func=ast.Name(id=target.PythonTargetTypes.PYTHON_BINARY.value),
            keywords=convert_kwargs_to_ast_keywords(**t.kwargs),
            args=[],
        )

    return


def convert_kwargs_to_ast_keywords(**kwargs) -> list[ast.keyword]:
    keywords: list[ast.keyword] = []
    for key, value in kwargs.items():
        if (keyword := convert_kwarg_to_ast_keyword(key, value)) is not None:
            keywords.append(keyword)
    return keywords


def convert_kwarg_to_ast_keyword(key: str, value: Union[bool, int, list, set, str]) -> Optional[ast.keyword]:
    if isinstance(value, Union[list, set]):
        values = sorted(list(value))
        return ast.keyword(
            arg=key,
            value=ast.List(elts=[ast.Constant(value=constant_value) for constant_value in values]),
        )
    elif isinstance(value, Union[str, int, bool]):
        return ast.keyword(arg=key, value=ast.Constant(value=value))

    # Note that a value can also be of type dict, but we should never need to write this to a BUILD file from here.
    return
