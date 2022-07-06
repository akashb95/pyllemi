KNOWN_DEPENDENCIES_KEY = "knownDependencies"
USE_GLOBS_AS_SRCS_KEY = "useGlobAsSrcs"


SCHEMA = {
    "type": "object",
    "properties": {
        KNOWN_DEPENDENCIES_KEY: {"type": "array", "items": {"$ref": "#/defs/knownDep"}},
        USE_GLOBS_AS_SRCS_KEY: {"type": "boolean"},
    },
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
