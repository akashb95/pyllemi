from typing import TypeVar

from config.schema import (
    KNOWN_DEPENDENCIES_KEY,
    KNOWN_NAMESPACES_KEY,
    USE_GLOBS_AS_SRCS_KEY,
)
from domain.plz.target.target import Target

MARSHALLED_CONFIG_VALUE_TYPE = TypeVar("MARSHALLED_CONFIG_VALUE_TYPE", bool, list[Target], Target)
MARSHALLED_CONFIG_TYPE = dict[str, MARSHALLED_CONFIG_VALUE_TYPE]


def merge(configs: list[MARSHALLED_CONFIG_TYPE]) -> MARSHALLED_CONFIG_TYPE:
    """

    :param configs: in descending order of precedence
    :return:
    """

    merged_use_globs_as_srcs = _merge_bool_property(USE_GLOBS_AS_SRCS_KEY, configs)
    merged_known_dependencies = _merge_dict_property(
        list(map(lambda x: getattr(x, KNOWN_DEPENDENCIES_KEY, {}), configs))
    )
    merged_known_namespaces = _merge_dict_property(list(map(lambda x: getattr(x, KNOWN_NAMESPACES_KEY, {}), configs)))
    return {
        USE_GLOBS_AS_SRCS_KEY: merged_use_globs_as_srcs,
        KNOWN_DEPENDENCIES_KEY: merged_known_dependencies,
        KNOWN_NAMESPACES_KEY: merged_known_namespaces,
    }


def _merge_bool_property(key: str, configs: list[MARSHALLED_CONFIG_TYPE], default: bool = False) -> bool:
    for config in configs:
        if (value := config.get(key, None)) is not None:
            return value
    return default


def _merge_dict_property(configs: list[MARSHALLED_CONFIG_VALUE_TYPE]) -> MARSHALLED_CONFIG_TYPE:
    merged_property = {}
    for config in reversed(configs):
        if not bool(config):
            # If this config is empty.
            continue
        merged_property |= config
    return merged_property
