import ast
from typing import Optional

from domain.plz.rule.rule import Rule, Types
from service.ast.converters.common import kwargs_to_ast_keywords


def to_ast_call_node(t: Rule) -> Optional[ast.Call]:
    if t.type_ == Types.PYTHON_LIBRARY:
        return ast.Call(
            func=ast.Name(id=Types.PYTHON_LIBRARY.value),
            keywords=kwargs_to_ast_keywords(**t.kwargs),
            args=[],
        )

    if t.type_ == Types.PYTHON_TEST:
        return ast.Call(
            func=ast.Name(id=Types.PYTHON_TEST.value),
            keywords=kwargs_to_ast_keywords(**t.kwargs),
            args=[],
        )

    if t.type_ == Types.PYTHON_BINARY:
        return ast.Call(
            func=ast.Name(id=Types.PYTHON_BINARY.value),
            keywords=kwargs_to_ast_keywords(**t.kwargs),
            args=[],
        )

    return
