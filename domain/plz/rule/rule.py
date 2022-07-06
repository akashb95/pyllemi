from abc import ABC, abstractmethod
from collections import OrderedDict
from enum import Enum
from typing import Optional


class Types(Enum):
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


class Rule(ABC):
    readable_attributes = frozenset({"srcs", "deps", "name", "main"})
    modifiable_attributes = frozenset({"deps"})

    def __init__(self, *, rule_name: str, **kwargs):
        self.rule_name = rule_name
        self.kwargs = OrderedDict(kwargs)
        return

    @property
    @abstractmethod
    def type_(self) -> Types:
        return Types.UNKNOWN

    def __str__(self) -> str:
        kwargs_repr = []
        for k, v in self.kwargs.items():
            kwargs_repr.append(f"{k} = {v}")

        return f"{self.rule_name}({', '.join(kwargs_repr)})"

    def __eq__(self, other: "Rule") -> bool:
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
