import ast
import enum
from dataclasses import dataclass, field
from typing import Optional


class PythonTargetTypes(enum.StrEnum):
    PYTHON_BINARY = "python_binary"
    PYTHON_LIBRARY = "python_library"
    PYTHON_TEST = "python_test"


@dataclass(kw_only=True)
class Target:
    name: str
    deps: set[str]
    other_kwargs: field(default_factory=dict)


@dataclass(kw_only=True)
class PythonBinary(Target):
    main: str


@dataclass(kw_only=True)
class PythonLibrary(Target):
    srcs: set[str]


@dataclass(kw_only=True)
class PythonTest(Target):
    srcs: set[str]


def convert_file_to_targets(source: str) -> tuple[list[Target], list[ast.AST]]:
    targets: list[Target] = []
    target_nodes: list[ast.AST] = []
    root = ast.parse(source)
    for node in ast.walk(root):
        if (target_definition := get_python_target(node)) is None:
            continue
        targets.append(target_definition)
        target_nodes.append(node)
    return targets, target_nodes


def get_python_target(node: ast.AST) -> Optional[Target]:
    if not isinstance(node, ast.Call):
        return None

    if not isinstance(node.func, ast.Name):
        return None

    if node.func.id not in (
            PythonTargetTypes.PYTHON_BINARY,
            PythonTargetTypes.PYTHON_LIBRARY,
            PythonTargetTypes.PYTHON_TEST,
    ):
        return None

    name: Optional[str] = None
    srcs: set[str] = set()
    deps: set[str] = set()
    target: Target

    if node.func.id == PythonTargetTypes.PYTHON_LIBRARY:
        other_target_kwargs = {}
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

            other_target_kwargs[keyword.arg] = keyword.value

        return PythonLibrary(name=name, deps=deps, srcs=srcs, other_kwargs=other_target_kwargs)

    elif node.func.id == PythonTargetTypes.PYTHON_TEST:
        other_target_kwargs = {}
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

            other_target_kwargs[keyword.arg] = keyword.value

        return PythonTest(name=name, deps=deps, srcs=srcs, other_kwargs=other_target_kwargs)

    elif node.func.id == PythonTargetTypes.PYTHON_BINARY:
        other_target_kwargs = {}
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

            other_target_kwargs[keyword.arg] = keyword.value

        return PythonBinary(name=name, deps=deps, main=main, other_kwargs=other_target_kwargs)
    return None
