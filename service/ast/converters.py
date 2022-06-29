import ast
from typing import Optional, Union

from adapters.plz_query import get_print
from domain.plz.rule.python import Binary, Library, Python, Test
from domain.plz.rule.rule import Rule, Types
from domain.plz.target.target import PlzTarget
from domain.targets.utils import is_ast_node_python_build_rule

BUILD_RULE_KWARG_VALUE_TYPE = Union[bool, int, list, set, str, ast.Call]


def from_ast_node_to_python_target(node: ast.Call, build_pkg_dir: str) -> Python:
    """

    :param node:
    :param build_pkg_dir: Relative path from reporoot
    :return: Domain repr of Python Rule
    """

    # Validation.
    if not isinstance(node, ast.Call):
        raise TypeError(f"AST node is of type {type(node).__name__}; expected {type(ast.Call()).__name__}")

    if not isinstance(node.func, ast.Name):
        raise TypeError(f"AST node func is of type {type(node.func).__name__}; expected {type(ast.Name())}")

    if node.func.id not in (
            Types.PYTHON_BINARY.value,
            Types.PYTHON_LIBRARY.value,
            Types.PYTHON_TEST.value,
    ):
        raise ValueError(f"BUILD rule call function is called '{node.func.id}', which is not a supported Python rule")

    # Conversion to domain representations.
    name: Optional[str] = None
    srcs: set[str] = set()
    deps: set[str] = set()

    if node.func.id == Types.PYTHON_LIBRARY.value:
        # Extract target name.
        if len(node.args) > 0:
            name_as_arg = node.args[0]
            if isinstance(name_as_arg, ast.Constant):
                name = name_as_arg.value
        for keyword in node.keywords:
            if name is None and keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                name = keyword.value.value

        if name is None:
            raise ValueError(f"could not compute name of target in {build_pkg_dir}")

        # Extract srcs and deps.
        for keyword in node.keywords:
            if keyword.arg == "srcs" and isinstance(keyword.value, ast.List):
                for elt in keyword.value.elts:
                    if not isinstance(elt, ast.Constant):
                        continue

                    srcs.add(elt.value)

            elif keyword.arg == "srcs":
                build_target_path = PlzTarget(f"//{build_pkg_dir}:{name}")
                srcs |= set(get_print(str(build_target_path), "srcs"))

            elif keyword.arg == "deps" and isinstance(keyword.value, ast.List):
                for elt in keyword.value.elts:
                    if not isinstance(elt, ast.Constant):
                        continue

                    deps.add(elt.value)

        return Library(name=name, deps=deps, srcs=srcs)

    if node.func.id == Types.PYTHON_TEST.value:
        # Extract target name.
        if len(node.args) > 0:
            name_as_arg = node.args[0]
            if isinstance(name_as_arg, ast.Constant):
                name = name_as_arg.value
        for keyword in node.keywords:
            if name is None and keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                name = keyword.value.value

        if name is None:
            raise ValueError(f"could not compute name of target in {build_pkg_dir}")

        # Extract srcs and deps.
        for keyword in node.keywords:
            if keyword.arg == "srcs" and isinstance(keyword.value, ast.List):
                for elt in keyword.value.elts:
                    if not isinstance(elt, ast.Constant):
                        continue

                    srcs.add(elt.value)

            elif keyword.arg == "srcs":
                build_target_path = PlzTarget(f"//{build_pkg_dir}:{name}")
                srcs |= set(get_print(build_target_path.with_tag("lib"), "srcs"))

            elif keyword.arg == "deps" and isinstance(keyword.value, ast.List):
                for elt in keyword.value.elts:
                    if not isinstance(elt, ast.Constant):
                        continue

                    deps.add(elt.value)

        return Test(name=name, deps=deps, srcs=srcs)

    if node.func.id == Types.PYTHON_BINARY.value:
        main: Optional[str] = None
        if len(node.args) > 0:
            name_as_arg = node.args[0]
            if isinstance(name_as_arg, ast.Constant):
                name = name_as_arg.value
        if len(node.args) > 1:
            main_as_arg = node.args[1]
            if isinstance(main_as_arg, ast.Constant):
                main = main_as_arg.value

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

        return Binary(name=name, deps=deps, main=main)


# noinspection PyTypeChecker
def from_ast_module_to_python_build_rule_occurrences(
    module: ast.Module,
    build_target: PlzTarget,
) -> dict[ast.Call, Python]:
    build_rule_ast_call_to_domain_target: dict[ast.Call, Python] = {}
    for ast_call in filter(lambda x: is_ast_node_python_build_rule(x), ast.walk(module)):
        if (target := from_ast_node_to_python_target(ast_call, build_target)) is None:
            continue

        build_rule_ast_call_to_domain_target[ast_call] = target
    return build_rule_ast_call_to_domain_target


def python_target_to_ast_call_node(t: Rule) -> Optional[ast.Call]:
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


def kwargs_to_ast_keywords(**kwargs) -> list[ast.keyword]:
    keywords: list[ast.keyword] = []
    for key, value in kwargs.items():
        if (keyword := kwarg_to_ast_keyword(key, value)) is not None:
            keywords.append(keyword)
    return keywords


def kwarg_to_ast_keyword(key: str, value: BUILD_RULE_KWARG_VALUE_TYPE) -> Optional[ast.keyword]:
    if isinstance(value, list) or isinstance(value, set):
        values = sorted(list(value))
        return ast.keyword(
            arg=key,
            value=ast.List(elts=[ast.Constant(value=constant_value) for constant_value in values]),
        )
    if isinstance(value, str) or isinstance(value, bool) or isinstance(value, int):
        return ast.keyword(arg=key, value=ast.Constant(value=value))
    if isinstance(value, ast.Call):
        return ast.keyword(arg=key, value=value)

    # Note that a value can also be of type dict, but we should never need to write this to a BUILD file from Pyllemi.
    return
