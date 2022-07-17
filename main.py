import logging
import os
import sys
from argparse import ArgumentParser
from typing import Collection

from adapters.plz_cli.query import (
    get_build_file_names,
    get_third_party_module_targets,
    get_python_moduledir,
    get_reporoot,
    run_plz_fmt,
)
from colorama import Fore
from common.custom_arg_types import existing_dir_arg_type
from config import config, known_dependencies, known_namespace_packages, merge
from domain.build_pkgs.build_pkg import BUILDPkg
from domain.plz.target.target import Target
from domain.python_import.stdlib.stdlib_modules import get_stdlib_module_names
from service.ast.converters.to_enriched_imports import ToEnrichedImports
from service.dependency.resolver import DependencyResolver
from service.python_import.node_collector import NodeCollector


# noinspection PyShadowingNames
def run(build_pkg_dir_paths: list[str]):
    """

    :param build_pkg_dir_paths: Relative to reporoot
    :return:
    """

    # Get 3rd Party libs and builtins, stdlibs and known imports.
    third_party_modules_targets: set[str] = set(get_third_party_module_targets())
    std_lib_modules: set[str] = get_stdlib_module_names()
    build_file_names: list[str] = get_build_file_names()

    build_pkgs: list[BUILDPkg] = []
    merged_config = {}
    for build_pkg_dir_path in build_pkg_dir_paths:
        merged_config = merge.merge(
            list(
                map(
                    config.unmarshal,
                    config.find_files_in_dir_hierarchy(build_pkg_dir_path),
                ),
            ),
        )
        build_pkgs.append(BUILDPkg(build_pkg_dir_path, set(build_file_names), merged_config))

    if len(build_pkgs) == 0:
        print(f"\n{Fore.GREEN}No BUILD package provided; no files modified.", file=sys.stdout)
        return

    known_deps: dict[str, Collection[Target]] = known_dependencies.get_from_config(merged_config)
    known_namespace_pkgs: dict[str, Target] = known_namespace_packages.get_from_config(merged_config)
    python_moduledir = get_python_moduledir()
    dependency_resolver = DependencyResolver(
        python_moduledir=python_moduledir,
        enricher=ToEnrichedImports(get_reporoot(), python_moduledir),
        std_lib_modules=std_lib_modules,
        available_third_party_module_targets=third_party_modules_targets,
        known_dependencies=known_deps,
        namespace_to_target=known_namespace_pkgs,
        nodes_collator=NodeCollector(),
    )

    modified_build_file_paths: list[str] = []
    for build_pkg in build_pkgs:
        build_pkg.resolve_deps_for_targets(dependency_resolver.resolve_deps_for_srcs)
        if build_pkg.has_uncommitted_changes():
            build_pkg.write_to_build_file()

        if build_pkg.has_been_modified:
            modified_build_file_paths.append(build_pkg.path())

    if modified_build_file_paths:
        run_plz_fmt(*modified_build_file_paths)
        print(f"{Fore.MAGENTA}📢 Modified BUILD files: {', '.join(modified_build_file_paths)}.", file=sys.stdout)
    else:
        print(f"\n{Fore.GREEN}No BUILD files were modified. Your imports were 👌 already.\n", file=sys.stdout)
    return


def to_relative_path_from_reporoot(path: str) -> str:
    if not os.path.isabs(path):
        as_abs_path = os.path.abspath(os.path.join(os.getcwd(), path))
    else:
        as_abs_path = path
    without_reporoot_prefix = as_abs_path.removeprefix(get_reporoot())
    if as_abs_path == without_reporoot_prefix:
        raise ValueError(f"{path} not within Plz repo")
    return without_reporoot_prefix.removeprefix(os.path.sep)


if __name__ == "__main__":
    import time
    from common.logger.logger import setup_logger

    parser = ArgumentParser()

    parser.add_argument(
        "build_pkg_dir",
        type=existing_dir_arg_type,
        nargs="+",
        help="BUILD package directories (relative to reporoot)",
    )
    parser.add_argument("--verbose", "-v", action="count", default=0)

    args = parser.parse_args()
    os.environ["PYLLEMI_LOG_LEVEL"] = str(max(0, logging.WARNING - (10 * args.verbose)))

    LOGGER = setup_logger(__file__)

    # Input sanitisation and change dir to reporoot
    build_pkg_dirs = list(map(to_relative_path_from_reporoot, set(args.build_pkg_dir)))
    os.chdir(get_reporoot())

    LOGGER.debug(f"resolving imports for {{{', '.join(build_pkg_dirs)}}}; cwd: {os.getcwd()}")

    start_time = time.time()
    run(build_pkg_dirs)
    duration = time.time() - start_time

    LOGGER.debug(f"Dependency target resolution for {{{', '.join(build_pkg_dirs)}}} took {duration} seconds.")
