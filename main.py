import os
from argparse import ArgumentParser
from logging import INFO

from common.logger.logger import setup_logger
from adapters.custom_arg_types import existing_file_arg_type
from domain.targets.resolver import Resolver
from domain.imports.stdlib_modules import get_stdlib_module_names
from domain.imports.nodes_collator import NodesCollator
from adapters.plz_query import (
    get_python_moduledir,
    get_reporoot,
    get_third_party_module_targets,
)

LOGGER = setup_logger(__file__, INFO)


def run(path_to_pyfile: str):
    # Get 3rd Party libs and builtins
    third_party_modules_targets: set[str] = set(get_third_party_module_targets())
    std_lib_modules: set[str] = get_stdlib_module_names()

    # Read pyfile.
    with open(path_to_pyfile) as f:
        code = f.read()

    # Get import nodes from Python file
    collator = NodesCollator()
    reporoot: str = get_reporoot()

    # Convert import nodes to plz targets
    plz_target_resolver = Resolver(
        reporoot,
        get_python_moduledir(),
        std_lib_modules,
        third_party_modules_targets,
    )
    plz_target_resolver.resolve(collator.collate(code=code, path=path_to_pyfile))

    for source in plz_target_resolver.custom_module_sources_without_targets:
        LOGGER.error(f"Import does not have a plz target: {source}")

    LOGGER.info(
        targets_as_deps(
            list(plz_target_resolver.third_party_module_imports) + list(plz_target_resolver.custom_module_targets)
        )
    )

    return


def targets_as_deps(targets):
    return "deps = {}".format(targets).replace("'", '"')


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "pyfile",
        type=existing_file_arg_type,
        help="Path to Python file from which to calculate plz deps.",
    )

    args = parser.parse_args()

    LOGGER.info(f"pyfile: {args.pyfile}; cwd: {os.getcwd()}")

    run(args.pyfile)
