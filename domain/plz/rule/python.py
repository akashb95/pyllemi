import ast
from typing import Union

from domain.plz.rule.rule import Rule, Types
from domain.plz.rule.utils import is_builtin_python_rule


class Python(Rule):
    def __init__(self, *, rule_name: str, name: str, srcs: Union[set[str], ast.Call], deps: set[str], **kwargs):
        super().__init__(rule_name=rule_name, name=name, srcs=srcs, deps=deps, **kwargs)
        return

    @property
    def type_(self) -> Types:
        if is_builtin_python_rule(self.rule_name):
            return Types(self.rule_name)
        return Types.UNKNOWN


class Binary(Python):
    def __init__(self, *, name: str, main: str, deps: set[str]):
        super().__init__(rule_name="python_binary", name=name, srcs=set(), deps=deps, main=main)
        return

    @property
    def type_(self) -> Types:
        return Types.PYTHON_BINARY


class Library(Python):
    glob_call = ast.Call(
        func=ast.Name(id="glob"),
        args=[ast.List(elts=[ast.Constant(value="*.py")])],
        keywords=[ast.keyword(arg="exclude", value=ast.List(elts=[ast.Constant(value="*_test.py")]))],
    )

    def __init__(self, *, name: str, srcs: set[str], deps: set[str], srcs_glob: bool = False):
        super().__init__(
            rule_name="python_library",
            name=name,
            srcs=self.glob_call if srcs_glob is True else srcs,
            deps=deps,
        )
        return

    @property
    def type_(self) -> Types:
        return Types.PYTHON_LIBRARY


class Test(Python):
    glob_call = ast.Call(
        func=ast.Name(id="glob"),
        args=[ast.List(elts=[ast.Constant(value="*_test.py")])],
        keywords=[],
    )

    def __init__(self, *, name: str, srcs: set[str], deps: set[str], srcs_glob: bool = False):
        super().__init__(
            rule_name="python_test",
            name=name,
            srcs=self.glob_call if srcs_glob is True else srcs,
            deps=deps,
        )
        return

    @property
    def type_(self) -> Types:
        return Types.PYTHON_TEST
