import json
import os
from dataclasses import dataclass, field
from typing import Any, Collection, Optional

import jsonschema

from config import known_dependencies, known_namespace_packages
from config.common import LOGGER
from config.schema import SCHEMA, CUSTOM_RULES_TO_MANAGE_KEY, USE_GLOBS_AS_SRCS_KEY, NO_PRUNE_KEY
from domain.plz.target.target import Target

CONFIG_FILE_NAME = ".pyllemi.json"


@dataclass
class Config:
    custom_rules_to_manage: set[str] = field(default_factory=set)
    known_deps: dict[str, Collection[Target]] = field(default_factory=dict)
    known_namespaces: dict[str, Target] = field(default_factory=dict)
    no_prune: Optional[bool] = None
    use_glob_as_srcs: Optional[bool] = None

    def __repr__(self) -> str:
        return (
            f"Config("
            f"custom_rules_to_manage={self.custom_rules_to_manage}, "
            f"known_deps={self.known_deps}, "
            f"known_namespaces={self.known_namespaces}, "
            f"no_prune={self.no_prune}, "
            f"use_glob_as_srcs={self.use_glob_as_srcs})"
            ")"
        )


def find_files_in_dir_hierarchy(path: str) -> list[str]:
    if not os.path.isdir(path):
        return []

    config_file_paths: list[str] = []
    for subdir in os.path.join(".", path).split(os.path.sep):
        if not os.path.isfile(config_file_path := os.path.join(subdir, CONFIG_FILE_NAME)):
            continue
        config_file_paths.append(config_file_path)

    # The most deeply nested config file path first -- return in order of descending precedence.
    config_file_paths.reverse()
    return config_file_paths


def unmarshal(path: str) -> Config:
    if not os.path.isfile(path):
        return Config()

    contents: str
    with open(path, "r") as config_file:
        contents = config_file.read()

    try:
        raw_config = json.loads(contents)
    except json.JSONDecodeError as e:
        LOGGER.critical("Could not read config file", exc_info=e)
        raise e

    _validate(raw_config)

    return Config(
        custom_rules_to_manage=raw_config.get(CUSTOM_RULES_TO_MANAGE_KEY, set()),
        known_deps=known_dependencies.get_from_config(raw_config),
        known_namespaces=known_namespace_packages.get_from_config(raw_config),
        no_prune=raw_config.get(NO_PRUNE_KEY, False),
        use_glob_as_srcs=raw_config.get(USE_GLOBS_AS_SRCS_KEY, False),
    )


def _validate(config: dict[str, Any]):
    try:
        jsonschema.validate(config, schema=SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        LOGGER.critical("Invalid JSON Schema for known dependencies", exc_info=e)
        raise e

    return
