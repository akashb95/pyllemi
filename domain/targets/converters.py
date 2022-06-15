import ast
from typing import Optional

from adapters.plz_query import get_print
import domain.ast.converters as ast_converters
from domain.targets.utils import is_ast_node_python_build_rule
from domain.targets.plz_target import PlzTarget
from domain.targets.python_target import PythonBinary, PythonLibrary, Python, PythonTargetTypes, PythonTest, Target


def from_ast_node_to_python_target(node: ast.Call, build_target_path: PlzTarget) -> Python:
    if not isinstance(node, ast.Call):
        raise TypeError(f"AST node is of type {type(node).__name__}; expected {type(ast.Call()).__name__}")

    if not isinstance(node.func, ast.Name):
        raise TypeError(f"AST node func is of type {type(node.func).__name__}; expected {type(ast.Name())}")

    if node.func.id not in (
            PythonTargetTypes.PYTHON_BINARY.value,
            PythonTargetTypes.PYTHON_LIBRARY.value,
            PythonTargetTypes.PYTHON_TEST.value,
    ):
        raise ValueError(f"BUILD rule call function is called '{node.func.id}', which is not a supported Python rule")

    name: Optional[str] = None
    srcs: set[str] = set()
    deps: set[str] = set()

    match node.func.id:
        case PythonTargetTypes.PYTHON_LIBRARY.value:
            if len(node.args) > 0:
                name_as_arg = node.args[0]
                if isinstance(name_as_arg, ast.Constant):
                    name = name_as_arg.value
            for keyword in node.keywords:
                if name is None and keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                    name = keyword.value.value

                elif keyword.arg == "srcs" and isinstance(keyword.value, ast.List):
                    for elt in keyword.value.elts:
                        if not isinstance(elt, ast.Constant):
                            continue

                        srcs.add(elt.value)

                elif keyword.arg == "srcs":
                    srcs |= set(get_print(str(build_target_path), "srcs"))

                elif keyword.arg == "deps" and isinstance(keyword.value, ast.List):
                    for elt in keyword.value.elts:
                        if not isinstance(elt, ast.Constant):
                            continue

                        deps.add(elt.value)

            return PythonLibrary(name=name, deps=deps, srcs=srcs)

        case PythonTargetTypes.PYTHON_TEST.value:
            if len(node.args) > 0:
                name_as_arg = node.args[0]
                if isinstance(name_as_arg, ast.Constant):
                    name = name_as_arg.value
            for keyword in node.keywords:
                if name is None and keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                    name = keyword.value.value

                elif keyword.arg == "srcs" and isinstance(keyword.value, ast.List):
                    for elt in keyword.value.elts:
                        if not isinstance(elt, ast.Constant):
                            continue

                        srcs.add(elt.value)

                elif keyword.arg == "srcs":
                    # TODO: query //path/to:_test#lib, where input is //path/to:test
                    srcs |= set(get_print(build_target_path.with_tag("lib"), "srcs"))
                    pass

                elif keyword.arg == "deps" and isinstance(keyword.value, ast.List):
                    for elt in keyword.value.elts:
                        if not isinstance(elt, ast.Constant):
                            continue

                        deps.add(elt.value)

            return PythonTest(name=name, deps=deps, srcs=srcs)

        case PythonTargetTypes.PYTHON_BINARY.value:
            main: Optional[str] = None
            if len(node.args) > 0:
                name_as_arg = node.args[0]
                if isinstance(name_as_arg, ast.Constant):
                    name = name_as_arg.value
            if len(node.args) > 1:
                main_as_arg = node.args[1]
                if isinstance(main_as_arg, ast.Constant):
                    name = main_as_arg.value

            for keyword in node.keywords:
                if name is None and keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                    name = keyword.value.value

                elif main is None and keyword.arg == "main" and isinstance(keyword.value, ast.Constant):
                    main = keyword.value.value

                elif keyword.arg == "deps" and isinstance(keyword.value, ast.List):
                    for elt in keyword.value.elts:
                        if not isinstance(elt, ast.Constant):
                            continue

                        deps.add(elt.value)

            return PythonBinary(name=name, deps=deps, main=main)


# noinspection PyTypeChecker
def from_ast_module_to_python_build_rule_occurrences(module: ast.Module, build_target: PlzTarget) -> dict[ast.Call, Python]:
    build_rule_ast_call_to_domain_target: dict[ast.Call, Python] = {}
    for ast_call in filter(lambda x: is_ast_node_python_build_rule(x), ast.walk(module)):
        if (target := from_ast_node_to_python_target(ast_call, build_target)) is None:
            continue

        build_rule_ast_call_to_domain_target[ast_call] = target
    return build_rule_ast_call_to_domain_target


def python_target_to_ast_call_node(t: Target) -> Optional[ast.Call]:
    if t.type_ == PythonTargetTypes.PYTHON_LIBRARY:
        return ast.Call(
            func=ast.Name(id=PythonTargetTypes.PYTHON_LIBRARY.value),
            keywords=ast_converters.kwargs_to_ast_keywords(**t.kwargs),
            args=[],
        )

    if t.type_ == PythonTargetTypes.PYTHON_TEST:
        return ast.Call(
            func=ast.Name(id=PythonTargetTypes.PYTHON_TEST.value),
            keywords=ast_converters.kwargs_to_ast_keywords(**t.kwargs),
            args=[],
        )

    if t.type_ == PythonTargetTypes.PYTHON_BINARY:
        return ast.Call(
            func=ast.Name(id=PythonTargetTypes.PYTHON_BINARY.value),
            keywords=ast_converters.kwargs_to_ast_keywords(**t.kwargs),
            args=[],
        )

    return
