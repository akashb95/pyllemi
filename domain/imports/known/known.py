from collections import defaultdict
from typing import Any

import jsonschema

from common.logger.logger import setup_logger
from domain.targets.plz_target import PlzTarget

LOGGER = setup_logger(__file__)

KNOWN_DEPENDENCIES_CONFIG_KEY = "knownDependencies"

_KNOWN_DEPENDENCIES_JSON_SCHEMA = {
    "type": "array",
    "items": {"$ref": "#/defs/knownDep"},
    "defs": {
        "knownDep": {
            "type": "object",
            "properties": {
                "module": {"type": "string", "minLength": 1},
                # Absolute Plz target patterns only.
                "plzTarget": {"type": "string", "pattern": "^//.+"},
            },
            "required": ["module", "plzTarget"],
            "additionalProperties": False,
        },
    },
}


def known_dependencies_from_config(config: dict[str, list[Any]]) -> dict[str, list[PlzTarget]]:
    if (known_dependencies := config.get(KNOWN_DEPENDENCIES_CONFIG_KEY)) is None:
        return {}

    try:
        jsonschema.validate(known_dependencies, schema=_KNOWN_DEPENDENCIES_JSON_SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        LOGGER.critical("Invalid JSON Schema for known dependencies", exc_info=e)
        raise e

    plz_target_lookup_by_module: defaultdict[str, list[PlzTarget]] = defaultdict(list)
    for known_dep in known_dependencies:
        plz_target_lookup_by_module[known_dep["module"]].append(PlzTarget(known_dep["plzTarget"]))

    LOGGER.debug(f"Known dependencies by module: {plz_target_lookup_by_module}")
    return plz_target_lookup_by_module
