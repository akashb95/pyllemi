import os
import json
import subprocess
from logging import INFO
from typing import Any, Optional

from common.logger.logger import setup_logger

LOGGER = setup_logger(__file__, INFO)


def get_plz_build_graph(pkg_dir: Optional[str] = None, args: Optional[list[str]] = None) -> dict[str, Any]:
    cmd = ["plz", "query", "graph"]
    if pkg_dir is not None:
        cmd.append(pkg_dir)
    if args is not None:
        cmd.extend(args)

    LOGGER.debug(f"Getting plz build graph with: {' '.join(cmd)}")

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    if proc.returncode != 0:
        LOGGER.error("Got a non-zero return code while trying to fetch plz graph", exc_info=proc.stderr)
        raise RuntimeError(proc.stderr)
    stdout: list[str] = []
    for line in proc.stdout:
        stdout.append(line.decode().rstrip())
    return json.loads("".join(stdout))


def get_third_party_modules(third_party_pkg_dir: str = os.path.join("third_party", "python")) -> set[str]:
    try:
        # Get all Python third-party libs' target names.
        query_args = ["--include", "py"]
        third_party_targets = get_plz_build_graph(third_party_pkg_dir, query_args)["packages"][third_party_pkg_dir][
            "targets"
        ].keys()
    except RuntimeError as e:
        LOGGER.error(f"Could not get build graph", exc_info=e)
        raise e
    except KeyError as e:
        LOGGER.error(f"Could not parse build graph", exc_info=e)
        raise e
    return set(filter(lambda x: not x.startswith("_"), third_party_targets))
