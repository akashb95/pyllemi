import ast
from typing import Optional

from adapters.plz_cli.query import get_print
from domain.plz.rule.python import Python, Binary
from domain.plz.rule.rule import Types
from domain.plz.target.target import Target

_BUILTIN_PYTHON_RULES = {
    Types.PYTHON_BINARY.value,
    Types.PYTHON_LIBRARY.value,
    Types.PYTHON_TEST.value,
}


def convert(node: ast.Call, *, build_pkg_dir: str, custom_rules_to_manage: set[str]) -> Python:
    # Validation.
    if not isinstance(node, ast.Call):
        raise TypeError(f"AST node is of type {type(node).__name__}; expected {type(ast.Call()).__name__}")

    if not isinstance(node.func, ast.Name):
        raise TypeError(f"AST node func is of type {type(node.func).__name__}; expected {type(ast.Name())}")

    if node.func.id not in _BUILTIN_PYTHON_RULES.union(custom_rules_to_manage):
        raise ValueError(f"BUILD rule call function is called '{node.func.id}', which is not a supported Python rule")

    if node.func.id in {Types.PYTHON_LIBRARY.value, Types.PYTHON_TEST.value}:
        name = _get_constant_kwarg_value(0, "name", node)
        if not name:
            raise ValueError(f"could not compute name of target in {build_pkg_dir}")

        # Extract srcs and deps.
        srcs = set(_get_list_kwarg_value(None, "srcs", node))
        if not srcs:
            # Test targets generate a hidden target with an additional tag.
            # This hidden target includes the name of the .py files.
            build_target_path = Target(f"//{build_pkg_dir}:{name}")
            try:
                # Builtin python_test rule has src files defined in a nested rule.
                srcs_from_plz_query_print = get_print(build_target_path.with_tag("lib"), "srcs")
                srcs |= set(srcs_from_plz_query_print)
            except RuntimeError:
                # Ignore errors if target not found - then this may not be a test target.
                pass
        if not srcs:
            build_target_path = Target(f"//{build_pkg_dir}:{name}")
            srcs |= set(get_print(str(build_target_path), "srcs"))
        deps = set(_get_list_kwarg_value(None, "deps", node))

        return Python(rule_name=node.func.id, name=name, deps=deps, srcs=srcs)

    if node.func.id == Types.PYTHON_BINARY.value:
        name = _get_constant_kwarg_value(0, "name", node)
        if not name:
            raise ValueError(f"could not compute name of Python binary target in {build_pkg_dir}")

        main = _get_constant_kwarg_value(1, "main", node)
        if not main:
            raise ValueError(f"could not compute main of Python binary target in {build_pkg_dir}")

        deps = set(_get_list_kwarg_value(None, "deps", node))

        return Binary(name=name, deps=deps, main=main)


def _get_constant_kwarg_value(arg_index: Optional[int], name: str, node: ast.Call) -> str:
    value: str = ""
    if arg_index and len(node.args) > arg_index:
        value_as_arg = node.args[arg_index]
        if isinstance(value_as_arg, ast.Constant):
            value = value_as_arg.value
    for keyword in node.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.Constant):
            value = keyword.value.value
            break
    return value


def _get_list_kwarg_value(arg_index: Optional[int], name: str, node: ast.Call) -> list:
    value: list = []
    if arg_index and len(node.args) > arg_index:
        value_as_arg = node.args[arg_index]
        if isinstance(value_as_arg, ast.Constant):
            value = value_as_arg.value

    for keyword in node.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.List):
            for elt in keyword.value.elts:
                if not isinstance(elt, ast.Constant):
                    continue

                value.append(elt.value)
            break
    return value
