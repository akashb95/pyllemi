from collections import OrderedDict
from enum import Enum
from typing import Optional


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
    readable_attributes = frozenset({"srcs", "deps", "name", "main"})
    modifiable_attributes = frozenset({"deps"})

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
            kwargs_repr.append(f"{k} = {v}")

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

    def __getitem__(self, item: str) -> Optional[set[str]]:
        if item not in self.readable_attributes:
            return None
        return self.kwargs.get(item)

    def __setitem__(self, key: str, value: set[str]) -> None:
        if self.kwargs[key] is None:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{key}'")

        if key not in self.modifiable_attributes:
            raise ValueError(f"'{key}' cannot be modified for a {self.__class__.__name__} object")
        self.kwargs[key] = value
        return


class Python(Target):
    def __init__(self, *, rule_name: str, name: str, srcs: set[str], deps: set[str], **kwargs):
        super().__init__(rule_name=rule_name, name=name, srcs=srcs, deps=deps, **kwargs)
        return


class PythonBinary(Python):
    def __init__(self, *, name: str, main: str, deps: set[str]):
        super().__init__(rule_name="python_binary", name=name, srcs=set(), deps=deps, main=main)
        return


class PythonLibrary(Python):
    def __init__(self, *, name: str, srcs: set[str], deps: set[str]):
        super().__init__(rule_name="python_library", name=name, srcs=srcs, deps=deps)
        return


class PythonTest(Python):
    def __init__(self, *, name: str, srcs: set[str], deps: set[str]):
        super().__init__(rule_name="python_test", name=name, srcs=srcs, deps=deps)
        return
