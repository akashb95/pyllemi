import ast
import logging
from typing import Iterator

import service.ast.converters as ast_converters
import service.ast.converters as target_converters
from common.logger.logger import setup_logger
from domain.plz.rule import python as domain_target
from domain.targets.utils import is_ast_node_python_build_rule


class BUILDFile:
    """
    Domain representation of a BUILD file, and its constituent build targets.
    Stores and provides methods to modify the AST representation of these targets.
    """

    def __init__(self, ast_repr: ast.Module):
        self._logger = setup_logger(__file__, logging.INFO)
        self._ast_repr: ast.Module = ast_repr
        self._modified_build_rule_to_domain_python_target: dict[ast.Call, domain_target.Python] = {}
        self._new_targets: list[domain_target.Python] = []

        self._modifiable_nodes: set[ast.Call] = self._get_all_existing_ast_python_build_rules()
        self._logger.info(f"Found {len(self._modifiable_nodes)} Python build targets.")
        return

    def _get_all_existing_ast_python_build_rules(self) -> set[ast.Call]:
        # noinspection PyTypeChecker
        return {node for node in ast.walk(self._ast_repr) if is_ast_node_python_build_rule(node)}

    def get_existing_ast_python_build_rules(self) -> Iterator[ast.Call]:
        for node in self._modifiable_nodes:
            yield node
        return

    def add_new_target(self, target_to_add: domain_target.Python):
        self._new_targets.append(target_to_add)
        return

    def register_modified_build_rule_to_python_target(self, build_rule: ast.Call, python_target: domain_target.Python):
        if build_rule not in self._modifiable_nodes:
            raise ValueError(
                "Programming Error: cannot modify given ast.Call node - it is not in the set of modifiable nodes"
            )
        self._modified_build_rule_to_domain_python_target[build_rule] = python_target
        return

    def dump_ast(self) -> str:
        self._add_new_targets_to_ast()
        self._reflect_changes_to_python_targets_in_ast()
        return ast.unparse(self._ast_repr)

    def _reflect_changes_to_python_targets_in_ast(self):
        for ast_call, domain_python_target in self._modified_build_rule_to_domain_python_target.items():
            _update_ast_call_keywords(
                ast_call,
                {"deps": domain_python_target.kwargs["deps"]},
            )
        return

    def _add_new_targets_to_ast(self):
        for new_target in self._new_targets:
            if (target_as_ast_call := target_converters.python_target_to_ast_call_node(new_target)) is not None:
                self._ast_repr.body.append(ast.Expr(value=target_as_ast_call))
        return

    @property
    def has_modifiable_nodes(self) -> bool:
        return len(self._modifiable_nodes) > 0

    def __str__(self) -> str:
        return self.dump_ast()


def _update_ast_call_keywords(
    node: ast.Call,
    key_to_value: dict[str, ast_converters.BUILD_RULE_KWARG_VALUE_TYPE],
) -> None:
    for i, k in enumerate(node.keywords):
        if k.arg in key_to_value:
            k.value = ast_converters.kwarg_to_ast_keyword(k.arg, key_to_value[k.arg]).value

    return
