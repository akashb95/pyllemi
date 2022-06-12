import ast
from typing import Optional

from domain.build_files.build_file import is_ast_node_python_build_rule
from domain.targets.target import PythonBinary, PythonLibrary, Python, PythonTargetTypes, PythonTest


def from_ast_node_to_python_target(node: ast.Call) -> Python:
    if not isinstance(node, ast.Call):
        raise TypeError(f"AST node is of type {type(node)}; expected {type(ast.Call())}")

    if not isinstance(node.func, ast.Name):
        raise TypeError(f"AST node func is of type {type(node.func)}; expected {type(ast.Name())}")

    if node.func.id not in (
            PythonTargetTypes.PYTHON_BINARY,
            PythonTargetTypes.PYTHON_LIBRARY,
            PythonTargetTypes.PYTHON_TEST,
    ):
        raise ValueError(f"BUILD rule call function is called '{node.func.id}', which is not a supported Python rule")

    name: Optional[str] = None
    srcs: set[str] = set()
    deps: set[str] = set()

    match node.func.id:
        case PythonTargetTypes.PYTHON_LIBRARY:
            for keyword in node.keywords:
                if keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                    name = keyword.value.value

                elif keyword.arg == "srcs" and isinstance(keyword.value, ast.List):
                    for elt in keyword.value.elts:
                        if not isinstance(elt, ast.Constant):
                            continue

                        srcs.add(elt.value)

                elif keyword.arg == "deps" and isinstance(keyword.value, ast.List):
                    for elt in keyword.value.elts:
                        if not isinstance(elt, ast.Constant):
                            continue

                        deps.add(elt.value)

            return PythonLibrary(name=name, deps=deps, srcs=srcs)

        case PythonTargetTypes.PYTHON_TEST:
            for keyword in node.keywords:
                if keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                    name = keyword.value.value

                elif keyword.arg == "srcs" and isinstance(keyword.value, ast.List):
                    for elt in keyword.value.elts:
                        if not isinstance(elt, ast.Constant):
                            continue

                        srcs.add(elt.value)

                elif keyword.arg == "deps" and isinstance(keyword.value, ast.List):
                    for elt in keyword.value.elts:
                        if not isinstance(elt, ast.Constant):
                            continue

                        deps.add(elt.value)

            return PythonTest(name=name, deps=deps, srcs=srcs)

        case PythonTargetTypes.PYTHON_BINARY:
            main: str = ""
            for keyword in node.keywords:
                if keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                    name = keyword.value.value

                elif keyword.arg == "main" and isinstance(keyword.value, ast.Constant):
                    main = keyword.value.value

                elif keyword.arg == "deps" and isinstance(keyword.value, ast.List):
                    for elt in keyword.value.elts:
                        if not isinstance(elt, ast.Constant):
                            continue

                        deps.add(elt.value)

            return PythonBinary(name=name, deps=deps, main=main)


# noinspection PyTypeChecker
def from_ast_module_to_python_build_rule_occurrences(module: ast.Module) -> dict[ast.Call, Python]:
    build_rule_ast_call_to_domain_target: dict[ast.Call, Python] = {}
    for ast_call in filter(lambda x: is_ast_node_python_build_rule(x), ast.walk(module)):
        if (target := from_ast_node_to_python_target(ast_call)) is None:
            continue

        build_rule_ast_call_to_domain_target[ast_call] = target
    return build_rule_ast_call_to_domain_target
