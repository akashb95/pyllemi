import ast

from domain.plz.rule.python import Types


def is_builtin_python_rule(item) -> bool:
    t = Types.UNKNOWN
    return item in t


def is_ast_node_python_build_rule(node: ast.AST, custom_rules_to_manage: set[str]) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and (is_builtin_python_rule(node.func.id) or node.func.id in custom_rules_to_manage)
    )


def get_ast_nodes_to_manage(root: ast.Module, custom_rules_to_manage: set[str]) -> set[ast.Call]:
    return {
        node
        for node in ast.walk(root)
        if is_ast_node_python_build_rule(node, custom_rules_to_manage=custom_rules_to_manage)
    }
