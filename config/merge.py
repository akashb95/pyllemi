from typing import TypeVar, Collection, Optional, Iterable

from config.config import Config
from domain.plz.target.target import Target

MARSHALLED_CONFIG_VALUE_TYPE = TypeVar(
    "MARSHALLED_CONFIG_VALUE_TYPE",
    bool,
    dict[str, Collection[Target]],
    dict[str, Target],
)
MARSHALLED_CONFIG_TYPE = dict[str, MARSHALLED_CONFIG_VALUE_TYPE]


def merge(configs: list[Config]) -> Config:
    """

    :param configs: in descending order of precedence
    :return:
    """

    effective_custom_rules_to_manage = _get_effective_list_property([c.custom_rules_to_manage for c in configs])
    merged_known_namespaces = _merge_dict_property([c.known_namespaces for c in configs])
    merged_known_dependencies = _merge_dict_property([c.known_deps for c in configs])
    effective_no_prune = _merge_bool_property([c.no_prune for c in configs])
    merged_use_globs_as_srcs = _merge_bool_property([c.use_glob_as_srcs for c in configs])
    return Config(
        custom_rules_to_manage=set(effective_custom_rules_to_manage),
        known_deps=merged_known_dependencies,
        known_namespaces=merged_known_namespaces,
        no_prune=effective_no_prune,
        use_glob_as_srcs=merged_use_globs_as_srcs,
    )


def _merge_bool_property(vals: list[Optional[bool]], default: bool = False) -> bool:
    for val in vals:
        if val is not None:
            return val
    return default


_LT = TypeVar("_LT")


def _get_effective_list_property(vals: Iterable[set[_LT]]) -> set[_LT]:
    """

    :param vals:
    :return: The non-zero value with the highest precedence. Note that this means that the values defined in configs of
        lower precedence are completely overridden, and NOT merged.
    """

    for val in vals:
        if val:
            return val
    return set()


def _merge_dict_property(configs: list[MARSHALLED_CONFIG_VALUE_TYPE]) -> MARSHALLED_CONFIG_VALUE_TYPE:
    merged_property = {}
    for config in reversed(configs):
        if not bool(config):
            # If this config is empty.
            continue
        merged_property |= config
    return merged_property
