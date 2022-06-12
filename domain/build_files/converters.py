import ast
from typing import Optional, Union

from domain.build_files.common_types import BUILD_RULE_KWARG_VALUE_TYPE
from domain.targets import target as domain_target


def python_target_to_ast_call_node(t: domain_target.Target) -> Optional[ast.Call]:
    if t.type_ == domain_target.PythonTargetTypes.PYTHON_LIBRARY:
        return ast.Call(
            func=ast.Name(id=domain_target.PythonTargetTypes.PYTHON_LIBRARY.value),
            keywords=kwargs_to_ast_keywords(**t.kwargs),
            args=[],
        )

    if t.type_ == domain_target.PythonTargetTypes.PYTHON_TEST:
        return ast.Call(
            func=ast.Name(id=domain_target.PythonTargetTypes.PYTHON_TEST.value),
            keywords=kwargs_to_ast_keywords(**t.kwargs),
            args=[],
        )

    if t.type_ == domain_target.PythonTargetTypes.PYTHON_BINARY:
        return ast.Call(
            func=ast.Name(id=domain_target.PythonTargetTypes.PYTHON_BINARY.value),
            keywords=kwargs_to_ast_keywords(**t.kwargs),
            args=[],
        )

    return


def kwargs_to_ast_keywords(**kwargs) -> list[ast.keyword]:
    keywords: list[ast.keyword] = []
    for key, value in kwargs.items():
        if (keyword := kwarg_to_ast_keyword(key, value)) is not None:
            keywords.append(keyword)
    return keywords


def kwarg_to_ast_keyword(key: str, value: BUILD_RULE_KWARG_VALUE_TYPE) -> Optional[ast.keyword]:
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
