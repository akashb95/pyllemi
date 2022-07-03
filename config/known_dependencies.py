from collections import defaultdict
from typing import Any

from config.common import LOGGER
from config.schema import KNOWN_DEPENDENCIES_KEY
from domain.plz.target.target import Target


def get_from_config(config: dict[str, list[Any]]) -> dict[str, list[Target]]:
    if (known_dependencies := config.get(KNOWN_DEPENDENCIES_KEY)) is None:
        return {}

    plz_target_lookup_by_module: defaultdict[str, list[Target]] = defaultdict(list)
    for known_dep in known_dependencies:
        plz_target_lookup_by_module[known_dep["module"]].append(Target(known_dep["plzTarget"]))

    LOGGER.debug(f"Known dependencies by module: {plz_target_lookup_by_module}")
    return plz_target_lookup_by_module
