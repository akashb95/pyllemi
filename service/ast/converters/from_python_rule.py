import ast

from domain.plz.rule.rule import Rule
from service.ast.converters.common import kwargs_to_ast_keywords


def convert(t: Rule) -> ast.Call:
    return ast.Call(
        func=ast.Name(id=t.rule_name),
        keywords=kwargs_to_ast_keywords(**t.kwargs),
        args=[],
    )
