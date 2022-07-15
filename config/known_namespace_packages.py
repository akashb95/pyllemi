from typing import Collection

from config.schema import KNOWN_NAMESPACES_KEY, UNMARSHALLED_CONFIG_TYPE
from domain.plz.target.target import Target


class DuplicateKnownNamespacePackagesError(ValueError):
    def __init__(self, duplicates: Collection[str]):
        self.duplicates = duplicates
        return

    def __str__(self) -> str:
        return f"found multiple entries in config for the following known namespace pkgs: {self.duplicates}"


def get_from_config(config: UNMARSHALLED_CONFIG_TYPE) -> dict[str, Target]:
    if (known_namespace_pkgs := config.get(KNOWN_NAMESPACES_KEY)) is None:
        return {}

    duplicates: set[str] = set()
    plz_target_lookup_by_namespace: dict[str, Target] = {}

    for known_namespace_pkg in known_namespace_pkgs:
        if known_namespace_pkg["namespace"] in plz_target_lookup_by_namespace:
            duplicates.add(known_namespace_pkg["namespace"])
            continue
        plz_target_lookup_by_namespace[known_namespace_pkg["namespace"]] = Target(known_namespace_pkg["plzTarget"])

    if duplicates:
        raise DuplicateKnownNamespacePackagesError(duplicates)

    return plz_target_lookup_by_namespace
