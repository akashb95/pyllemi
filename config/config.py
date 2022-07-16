import json
import os
from typing import Any

import jsonschema

from config.common import LOGGER
from config.schema import SCHEMA

CONFIG_FILE_NAME = ".pyllemi.json"


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


def unmarshal(path: str) -> dict[str, Any]:
    if not os.path.isfile(path):
        return {}

    contents: str
    with open(path, "r") as config_file:
        contents = config_file.read()

    try:
        config = json.loads(contents)
    except json.JSONDecodeError as e:
        LOGGER.critical("Could not read config file", exc_info=e)
        raise e

    _validate(config)

    return config


def _validate(config: dict[str, Any]):
    try:
        jsonschema.validate(config, schema=SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        LOGGER.critical("Invalid JSON Schema for known dependencies", exc_info=e)
        raise e
