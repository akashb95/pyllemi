import os
from argparse import ArgumentParser
from logging import INFO

from common.logger.logger import setup_logger
from adapters.custom_arg_types import existing_file_arg_type
from imports.stdlib_modules import get_stdlib_module_names
from imports.nodes_collator import NodesCollator
from adapters.plz_query_graph import (
    get_python_moduledir,
    get_reporoot,
    get_third_party_modules,
)
from imports.node_transformer import ToAbsoluteImportPaths
from converters.build_targets import third_party_import_to_plz_target

LOGGER = setup_logger(__file__, INFO)
THIRD_PARTY_PKG_DIR_PATH = os.path.join("third_party", "python3")


def run(path_to_pyfile: str):
    # Get 3rd Party libs and builtins
    third_party_modules: set[str] = set(get_third_party_modules())
    std_lib_modules: set[str] = get_stdlib_module_names()

    # Read pyfile.
    with open(path_to_pyfile) as f:
        code = f.read()

    # Get import nodes from Python file
    collator = NodesCollator()
    reporoot: str = get_reporoot()
    to_absolute_import_paths = ToAbsoluteImportPaths(reporoot)
    custom_module_imports: list[str] = []
    third_party_module_imports: list[str] = []
    third_party_dep_targets: list[str] = []
    for import_node in collator.collate(code=code, path=path_to_pyfile):
        for abs_import_paths in to_absolute_import_paths.transform(import_node):
            for abs_import_path in abs_import_paths:
                # Filter out stdlib modules.
                top_level_module_name = get_top_level_module_name(abs_import_path)
                if top_level_module_name in std_lib_modules:
                    LOGGER.info(f"Found import of a standard lib module: {top_level_module_name}")
                    continue

                # If import is a 3rd party library, then only the top-level module name is required.
                if top_level_module_name in third_party_modules:
                    LOGGER.info(f"Found import of a third party module: {top_level_module_name}")
                    third_party_module_imports.append(top_level_module_name)
                    continue

                LOGGER.info(f"Found import of a custom lib module: {abs_import_path}")
                custom_module_imports.append(abs_import_path)

        third_party_dep_targets.extend(
            list(
                map(
                    lambda x: third_party_import_to_plz_target(x, get_python_moduledir()),
                    third_party_module_imports,
                )
            ),
        )
        for target in third_party_dep_targets:
            LOGGER.info(f"Third party dep found: {target}")

        # TODO: find usages of subpackages and find innermost plz targets of such usages.
        # TODO: map custom lib imports to plz targets.

        # TODO: output error logs when no targets found for imports.
        ...

    return


def get_top_level_module_name(abs_import_path: str) -> str:
    return abs_import_path.split(".", maxsplit=1)[0] if "." in abs_import_path else abs_import_path


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
