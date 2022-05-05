import os
import json
import re
import subprocess
from collections import namedtuple
from functools import cache, lru_cache
from logging import INFO
from typing import Any, AnyStr, IO, Optional

from common.logger.logger import setup_logger

LOGGER = setup_logger(__file__, INFO)

WhatInputsResult = namedtuple("WhatInputsResult", ["plz_targets", "targetless_paths"])


@cache
def get_config(specifier: str) -> list[str]:
    cmd = ["plz", "query", "config", specifier]

    LOGGER.debug(f"Getting plz config for {specifier}")

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    if not _is_success_return_code(proc.returncode):
        LOGGER.error(f"Got a non-zero return code while trying to fetch plz config for {specifier}")
        raise RuntimeError(proc.stderr)

    stdout: list[str] = []
    for line in proc.stdout:
        stdout.append(line.decode().rstrip())

    return stdout


@lru_cache(1)
def get_python_moduledir() -> str:
    get_config_output = get_config("python.moduledir")
    assert len(get_config_output) == 1, (
        "expected to only find 1 python moduledir,"
        f"but found {len(get_config_output)}: {get_config_output}"
    )
    return get_config_output[0]


@cache
def get_plz_build_graph(
        pkg_dir: Optional[str] = None,
        args: Optional[list[str]] = None,
) -> dict[str, Any]:
    cmd = ["plz", "query", "graph"]
    if pkg_dir is not None:
        cmd.append(pkg_dir)
    if args is not None:
        cmd.extend(args)

    LOGGER.debug(f"Getting plz build graph with: {' '.join(cmd)}")

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    if not _is_success_return_code(proc.returncode):
        LOGGER.error(
            "Got a non-zero return code while trying to fetch plz graph",
            exc_info=proc.stderr,
        )
        raise RuntimeError(proc.stderr)
    stdout: list[str] = []
    for line in proc.stdout:
        stdout.append(line.decode().rstrip())
    return json.loads("".join(stdout))


@cache
def get_whatinputs(paths_from_reporoot: list[str]) -> WhatInputsResult:
    """

    :param paths_from_reporoot: a Collection of paths to python modules.
    :return: a list of plz targets
    """

    if len(paths_from_reporoot) == 0:
        return WhatInputsResult([], [])

    cmd = ["plz", "whatinputs", *paths_from_reporoot]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    if not _is_success_return_code(proc.returncode):
        LOGGER.error(
            "Got a non-zero return code while trying to execute `plz whatinputs`",
            exc_info=proc.stderr,
        )
        raise RuntimeError(proc.stderr)

    stdout = _convert_list_of_bytes_to_list_of_strs(proc.stdout)

    targetless_path_msg_pattern = re.compile(
        r"Error: '(.+)' is not a source to any current target",
    )
    plz_targets: list[str] = []
    targetless_paths: list[str] = []
    for line in stdout:
        if (match := targetless_path_msg_pattern.match(line)) is not None:
            targetless_paths.append(match.group(1))

        elif line.startswith("//"):
            plz_targets.append(line)

        else:
            LOGGER.warning(f"plz whatinputs got unexpected output in stdout: {line}")

    return WhatInputsResult(plz_targets, targetless_paths)


@cache
def get_reporoot() -> str:
    cmd = ["plz", "query", "reporoot"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    if not _is_success_return_code(proc.returncode):
        LOGGER.error(
            "Got a non-zero return code while trying to fetch plz project root",
            exc_info=proc.stderr,
        )
        raise RuntimeError(proc.stderr)

    stdout: list[str] = []
    for line in proc.stdout:
        stdout.append(line.decode().rstrip())

    assert len(stdout) == 1, f"Unexpected output while getting reporoot: {stdout}"
    return stdout[0]


@lru_cache(1)
def get_third_party_modules() -> list[str]:
    return get_all_targets(
        [
            # Convert third_party.moduledir -> third_party/moduledir/...
            os.path.join(
                get_python_moduledir().replace(".", os.path.sep),
                "...",
            )
        ]
    )


def get_all_targets(
        plz_pkg_dirs: list[str],
        query_args: Optional[list[str]] = None,
) -> list[str]:
    query_args = [] if query_args is None else query_args

    cmd = ["plz", "query", "alltargets", *query_args, *plz_pkg_dirs]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    if not _is_success_return_code(proc.returncode):
        LOGGER.error(
            "Got a non-zero return code while trying to run `plz query alltargets`",
            exc_info=proc.stderr,
        )
        raise RuntimeError(proc.stderr)

    stdout: list[str] = []
    for line in proc.stdout:
        stdout.append(line.decode().rstrip())
    return stdout


def _convert_list_of_bytes_to_list_of_strs(input_: Optional[IO[AnyStr]]) -> list[str]:
    if input_ is None:
        return []

    output: list[str] = []
    for line in input_:
        output.append(line.decode().rstrip())
    return output


def _is_success_return_code(return_code: Optional[int]) -> bool:
    return return_code is None or return_code == 0
