from typing import Union


CUSTOM_RULES_TO_MANAGE_KEY: str = "customRulesToManage"
KNOWN_DEPENDENCIES_KEY: str = "knownDependencies"
KNOWN_NAMESPACES_KEY: str = "knownNamespaces"
NO_PRUNE_KEY: str = "noPrune"
USE_GLOBS_AS_SRCS_KEY: str = "useGlobAsSrcs"

UNMARSHALLED_CONFIG_TYPE = dict[str, Union[bool, list[dict[str, str]]]]

SCHEMA = {
    "type": "object",
    "properties": {
        CUSTOM_RULES_TO_MANAGE_KEY: {"type": "array", "items": {"type": "string", "minLength": 1}},
        KNOWN_DEPENDENCIES_KEY: {"type": "array", "items": {"$ref": "#/defs/knownDep"}},
        KNOWN_NAMESPACES_KEY: {"type": "array", "items": {"$ref": "#/defs/knownNamespacePkg"}},
        NO_PRUNE_KEY: {"type": "boolean"},
        USE_GLOBS_AS_SRCS_KEY: {"type": "boolean"},
    },
    "defs": {
        "knownDep": {
            "type": "object",
            "properties": {
                "module": {"type": "string", "minLength": 1},
                "plzTarget": {"type": "string", "pattern": "^//.+"},
            },
            "required": ["module", "plzTarget"],
            "additionalProperties": False,
        },
        "knownNamespacePkg": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "pattern": r"\w[\w\.]*",  # A valid absolute Python import.
                },
                "plzTarget": {"type": "string", "pattern": r"^//.+"},
            },
            "required": ["namespace", "plzTarget"],
            "additionalProperties": False,
        },
    },
}
