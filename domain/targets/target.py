from enum import Enum
from collections import OrderedDict


class PythonTargetTypes(Enum):
    UNKNOWN = "unknown"
    PYTHON_BINARY = "python_binary"
    PYTHON_LIBRARY = "python_library"
    PYTHON_TEST = "python_test"

    @classmethod
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class Target:
    modifiable_attributes = frozenset({"srcs", "deps"})

    def __init__(self, *, rule_name: str, **kwargs):
        self.rule_name = rule_name
        self.kwargs = OrderedDict(kwargs)
        return

    @property
    def type_(self) -> PythonTargetTypes:
        try:
            return PythonTargetTypes(self.rule_name)
        except ValueError:
            return PythonTargetTypes.UNKNOWN

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


class Python(Target):
    def __init__(self, *, rule_name: str, name: str, srcs: set[str], deps: set[str], **kwargs):
        super().__init__(rule_name=rule_name, name=name, srcs=srcs, deps=deps, **kwargs)
        return


class PythonBinary(Python):
    def __init__(self, *, name: str, main: str, deps: set[str]):
        super().__init__(rule_name="python_library", name=name, srcs=set(), deps=deps, main=main)
        return


class PythonLibrary(Python):
    def __init__(self, *, name: str, srcs: set[str], deps: set[str]):
        super().__init__(rule_name="python_library", name=name, srcs=srcs, deps=deps)
        return


class PythonTest(Python):
    def __init__(self, *, name: str, srcs: set[str], deps: set[str]):
        super().__init__(rule_name="python_test", name=name, srcs=srcs, deps=deps)
        return


# def convert_file_to_targets(source: str) -> tuple[list[Target], list[ast.AST]]:
#     targets: list[Target] = []
#     target_nodes: list[ast.AST] = []
#     root = ast.parse(source)
#     for node in ast.walk(root):
#         if (target_definition := get_python_target(node)) is None:
#             continue
#         targets.append(target_definition)
#         target_nodes.append(node)
#     return targets, target_nodes
