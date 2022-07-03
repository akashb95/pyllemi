import json
import os
from typing import Any

import jsonschema

from config.common import LOGGER
from config.schema import SCHEMA


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
