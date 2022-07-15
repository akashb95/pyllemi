from typing import Union


KNOWN_DEPENDENCIES_KEY = "knownDependencies"
KNOWN_NAMESPACES_KEY = "knownNamespaces"
USE_GLOBS_AS_SRCS_KEY = "useGlobAsSrcs"

UNMARSHALLED_CONFIG_TYPE = dict[str, Union[bool, list[dict[str, str]]]]

SCHEMA = {
    "type": "object",
    "properties": {
        KNOWN_DEPENDENCIES_KEY: {"type": "array", "items": {"$ref": "#/defs/knownDep"}},
        KNOWN_NAMESPACES_KEY: {"type": "array", "items": {"$ref": "#/defs/knownNamespacePkg"}},
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
        },
    },
}
