import ast
import logging
from typing import Optional, Union

from common.logger.logger import setup_logger
from domain.targets import target as domain_target

_BUILD_RULE_KWARG_VALUE_TYPE = Union[bool, int, list, set, str]


class BUILDFile:
    def __init__(self, ast_repr: ast.Module):
        self._logger = setup_logger(__file__, logging.INFO)
        self._ast_repr: ast.Module = ast_repr
        self._modified_build_rule_to_domain_python_target: dict[ast.Call, domain_target.Python] = {}
        self._new_targets: list[domain_target.Python] = []
        return

    def add_target(self, target_to_add: domain_target.Python):
        self._new_targets.append(target_to_add)
        return

    def register_modified_build_rule_to_python_target(self, build_rule: ast.Call, python_target: domain_target.Python):
        self._modified_build_rule_to_domain_python_target[build_rule] = python_target
        return

    def dump_ast(self) -> str:
        self._add_new_targets_to_ast()
        self._reflect_changes_to_python_targets_in_ast()
        return ast.unparse(self._ast_repr)

    def _reflect_changes_to_python_targets_in_ast(self):
        for ast_call, domain_python_target in self._modified_build_rule_to_domain_python_target.items():
            _update_ast_call_keywords(
                ast_call,
                {"deps": domain_python_target.kwargs["deps"], "srcs": domain_python_target.kwargs["srcs"]},
            )
        return

    def _add_new_targets_to_ast(self):
        for new_target in self._new_targets:
            if (target_as_ast_call := convert_python_target_to_ast_call_node(new_target)) is not None:
                self._ast_repr.body.append(ast.Expr(value=target_as_ast_call))
        return


def convert_python_target_to_ast_call_node(t: domain_target.Target) -> Optional[ast.Call]:
    if t.type_ == domain_target.PythonTargetTypes.PYTHON_LIBRARY:
        return ast.Call(
            func=ast.Name(id=domain_target.PythonTargetTypes.PYTHON_LIBRARY.value),
            keywords=convert_kwargs_to_ast_keywords(**t.kwargs),
            args=[],
        )

    if t.type_ == domain_target.PythonTargetTypes.PYTHON_TEST:
        return ast.Call(
            func=ast.Name(id=domain_target.PythonTargetTypes.PYTHON_TEST.value),
            keywords=convert_kwargs_to_ast_keywords(**t.kwargs),
            args=[],
        )

    if t.type_ == domain_target.PythonTargetTypes.PYTHON_BINARY:
        return ast.Call(
            func=ast.Name(id=domain_target.PythonTargetTypes.PYTHON_BINARY.value),
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


def convert_kwarg_to_ast_keyword(key: str, value: _BUILD_RULE_KWARG_VALUE_TYPE) -> Optional[ast.keyword]:
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


def is_ast_node_python_build_rule(node: ast.AST) -> bool:
    return (
            isinstance(node, ast.Call) and
            isinstance(node.func, ast.Name) and
            node.func.id in domain_target.PythonTargetTypes
    )


def _update_ast_call_keywords(node: ast.Call, key_to_value: dict[str, _BUILD_RULE_KWARG_VALUE_TYPE]) -> None:
    for i, k in enumerate(node.keywords):
        if k.arg in key_to_value:
            k.value = convert_kwarg_to_ast_keyword(k.arg, key_to_value[k.arg]).value

    return
