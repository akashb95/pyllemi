import ast
from typing import Optional

from adapters.plz_cli.query import get_print
from domain.plz.rule.python import Python, Library, Test, Binary
from domain.plz.rule.rule import Types
from domain.plz.target.target import Target


def convert(node: ast.Call, build_pkg_dir: str) -> Python:
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
                build_target_path = Target(f"//{build_pkg_dir}:{name}")
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
                build_target_path = Target(f"//{build_pkg_dir}:{name}")
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
