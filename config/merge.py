from typing import TypeVar, Collection, Optional

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
    merged_use_globs_as_srcs = _merge_bool_property([c.use_glob_as_srcs for c in configs])
    merged_known_namespaces = _merge_dict_property([c.known_namespaces for c in configs])
    merged_known_dependencies = _merge_dict_property([c.known_deps for c in configs])
    return Config(
        known_deps=merged_known_dependencies,
        known_namespaces=merged_known_namespaces,
        use_glob_as_srcs=merged_use_globs_as_srcs,
    )


def _merge_bool_property(vals: list[Optional[bool]], default: bool = False) -> bool:
    for val in vals:
        if val is not None:
            return val
    return default


def _merge_dict_property(configs: list[MARSHALLED_CONFIG_VALUE_TYPE]) -> MARSHALLED_CONFIG_VALUE_TYPE:
    merged_property = {}
    for config in reversed(configs):
        if not bool(config):
            # If this config is empty.
            continue
        merged_property |= config
    return merged_property
