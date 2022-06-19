import ast

from domain.targets.python_target import PythonTargetTypes


def is_ast_node_python_build_rule(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and is_python_target_type(node.func.id)


def is_python_target_type(item):
    t = PythonTargetTypes.UNKNOWN
    return item in t
