import os
from argparse import ArgumentParser
from logging import INFO

from common.logger.logger import setup_logger
from adapters.custom_arg_types import existing_file_arg_type
from imports.py_import import Import, to_whatinputs_input
from imports.stdlib_modules import get_stdlib_module_names
from imports.nodes_collator import NodesCollator
from adapters.plz_query_graph import (
    get_python_moduledir,
    get_reporoot,
    get_third_party_module_targets,
    get_whatinputs,
)
from imports.node_transformer import ToAbsoluteImports

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
    to_absolute_imports = ToAbsoluteImports(reporoot, get_python_moduledir())
    custom_module_imports: list[Import] = []
    third_party_module_imports: set[str] = set()
    custom_module_targets: set[str] = set()
    custom_module_sources_without_targets: set[str] = set()

    for import_node in collator.collate(code=code, path=path_to_pyfile):
        # TODO: refactor into PlzTargetResolver
        for abs_imports in to_absolute_imports.transform(import_node):
            for abs_import in abs_imports:

                # Filter out stdlib modules.
                top_level_module_name = get_top_level_module_name(abs_import.import_)
                if top_level_module_name in std_lib_modules:
                    LOGGER.info(f"Found import of a standard lib module: {top_level_module_name}")
                    continue

                # Resolve 3rd-party library targets.
                possible_third_party_module_target = (
                    f"//{get_python_moduledir()}:{top_level_module_name}".replace(".", "/")
                )
                if possible_third_party_module_target in third_party_modules_targets:
                    third_party_module_imports.add(possible_third_party_module_target)
                    continue

                LOGGER.debug(f"Found import of a custom lib module: {abs_import.import_}")
                custom_module_imports.append(abs_import)

                if (whatinputs_input := to_whatinputs_input(abs_import)) is not None:
                    whatinputs_result = get_whatinputs(whatinputs_input)
                    custom_module_targets |= whatinputs_result.plz_targets
                    custom_module_sources_without_targets |= whatinputs_result.targetless_paths

    for target in custom_module_sources_without_targets:
        LOGGER.warning(f"Import does not have a plz target: {target}")

        # TODO: find usages of subpackages and find innermost plz targets of such usages.

        # TODO: output error logs when no targets found for imports.
        ...

    LOGGER.info(targets_as_deps(list(third_party_module_imports) + list(custom_module_targets)))

    return


def get_top_level_module_name(abs_import_path: str) -> str:
    return abs_import_path.split(".", maxsplit=1)[0] if "." in abs_import_path else abs_import_path


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

    LOGGER.warning(f"pyfile: {args.pyfile}; cwd: {os.getcwd()}")

    run(args.pyfile)
