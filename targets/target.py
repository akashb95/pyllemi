import ast
from enum import Enum
from typing import Optional
from collections import OrderedDict


class PythonTargetTypes(Enum):
    PYTHON_BINARY = "python_binary"
    PYTHON_LIBRARY = "python_library"
    PYTHON_TEST = "python_test"


class Target:
    def __init__(self, *, rule_name: str, **kwargs):
        self.rule_name = rule_name
        self.kwargs = OrderedDict(kwargs)
        return

    def __str__(self) -> str:
        kwargs_repr = []
        for k, v in self.kwargs.items():
            kwargs_repr.append(f'{k} = {v}')

        return f"{self.rule_name}({', '.join(kwargs_repr)})"

    def __eq__(self, other: "Target") -> bool:
        if self.rule_name != other.rule_name:
            return False

        for k, v in self.kwargs.items():
            if (other_v := other.kwargs.get(k)) is None:
                return False

            if v != other_v:
                return False

        return True


class PythonTarget(Target):
    def __init__(self, *, rule_name: str, name: str, srcs: set[str], deps: set[str], **kwargs):
        super().__init__(rule_name=rule_name, name=name, srcs=srcs, deps=deps, **kwargs)
        return


class PythonLibrary(PythonTarget):
    def __init__(self, *, name: str, srcs: set[str], deps: set[str], **kwargs):
        super().__init__(rule_name="python_library", name=name, srcs=srcs, deps=deps, **kwargs)
        return


class PythonTest(PythonTarget):
    def __init__(self, *, name: str, srcs: set[str], deps: set[str], **kwargs):
        super().__init__(rule_name="python_test", name=name, srcs=srcs, deps=deps, **kwargs)
        return


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

    # elif node.func.id == PythonTargetTypes.PYTHON_BINARY:
    #     other_target_kwargs = {}
    #     main: str = ""
    #     for keyword in node.keywords:
    #         if keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
    #             name = keyword.value.value
    #
    #         elif keyword.arg == "main" and isinstance(keyword.value, ast.Constant):
    #             main = keyword.value.value
    #
    #         elif keyword.arg == "deps" and isinstance(keyword.value, ast.List):
    #             for elt in keyword.value.elts:
    #                 if not isinstance(elt, ast.Constant):
    #                     continue
    #
    #                 deps.add(elt.value)
    #
    #         other_target_kwargs[keyword.arg] = keyword.value
    #
    #     return PythonBinary(name=name, deps=deps, main=main, other_kwargs=other_target_kwargs)
    return None
