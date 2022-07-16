import ast
import logging
import os.path
from typing import Callable, Collection, Optional, Any

import service.ast.converters.to_python_rule
from adapters.os.new_build_pkg_creator import NewBuildPkgCreator
from common.logger.logger import setup_logger
from domain.build_files.build_file import BUILDFile
from domain.plz.rule.python import Library, Test
from domain.plz.target.target import Target


class BUILDPkg:
    """
    This class is used to manage BUILD targets in the given BUILD package.
    Where necessary, it will create new packages in the given path, and add new targets to it.
    It provides a method to perform dependency resolution by means of an injected callable.

    Usage::

        build_pkg = BUILDPkg()
        build_pkg.resolve_deps_for_target(domain_targets.resolver.resolve)

    """

    def __init__(self, dir_path_relative_to_reporoot: str, build_file_names: Collection[str], config: dict[str, Any]):
        self._logger = setup_logger(__file__, logging.INFO)
        self._uncommitted_changes: bool = False
        self._dir_path: str = dir_path_relative_to_reporoot
        self._build_file_names = build_file_names
        self._build_file_names_sorted_by_len = sorted(list(self._build_file_names), key=lambda x: len(x))

        self._build_file = BUILDFile(ast.Module(body=[], type_ignores=[]))

        self._new_pkg_creator = NewBuildPkgCreator(
            self._dir_path,
            set(build_file_names),
            config.get("useGlobAsSrcs", False),
        )
        self._this_pkg_build_file_path: str = ""

        self._has_been_modified = False

        self._initialise()
        return

    def _initialise(self):
        # If this is a directory with no BUILD file, create one and write to FS.
        # This must be done before dependency resolution in case multiple BUILDPkg
        # instances are being orchestrated at the same time by the caller, and
        # the instances have dependencies between them.
        if self._is_new_pkg():
            self._infer_targets_and_add_to_build_file()
            if self._uncommitted_changes:
                self.write_to_build_file()
            else:
                self._logger.warning(f"No BUILD file or Python modules found in {self._dir_path}")
                return

        # There should now already be a BUILD file within this directory; read it and
        # load existing Python target declarations into domain representations.
        self._parse_existing_python_targets()
        # If there are no existing Python targets declared, try and infer them,
        # and write them to the build file.
        if not self._build_file.has_modifiable_nodes:
            self._infer_targets_and_add_to_build_file()
            if self._uncommitted_changes:
                self.write_to_build_file()
        return

    def resolve_deps_for_targets(self, deps_resolver_fn: Callable[[Target, set[str]], set[Target]]) -> None:
        if not self._build_file.has_modifiable_nodes:
            return

        for node in self._build_file.get_existing_ast_python_build_rules():
            as_python_target = service.ast.converters.to_python_rule.convert(node, self._dir_path)
            self._logger.debug(f"Found target in {self._this_pkg_build_file_path}: {as_python_target}")

            resolved_deps = deps_resolver_fn(
                Target(f"//{self._dir_path}:{as_python_target['name']}"),
                # Only a python_binary target has the main attribute; all other Python targets will have srcs.
                # The occurrence of the 2 different attributes are mutually exclusive.
                as_python_target["srcs"] or [as_python_target["main"]],
            )

            if (
                new_deps := set(map(lambda plz_target: plz_target.simplify(self._dir_path), resolved_deps))
            ) == as_python_target["deps"]:
                # No need to update dependencies if there is no change
                continue

            as_python_target["deps"] = new_deps
            self._build_file.register_modified_build_rule_to_python_target(node, as_python_target)
            self._uncommitted_changes = True
        return

    def _is_new_pkg(self) -> bool:
        for build_file_name in self._build_file_names:
            if os.path.isfile(path := os.path.join(self._dir_path, build_file_name)):
                self._this_pkg_build_file_path = path
                self._logger.debug(f"Found existing BUILD file: {path}")
                return False

        for build_file_name in self._build_file_names_sorted_by_len:
            # Preference to shorter BUILD file names.
            if not os.path.isdir(path := os.path.join(self._dir_path, build_file_name)):
                self._this_pkg_build_file_path = path
                break
        return True

    def _infer_targets_and_add_to_build_file(self):
        python_library: Optional[Library]
        python_test: Optional[Test]
        python_library, python_test = self._new_pkg_creator.infer_py_targets()

        if python_library is None and python_test is None:
            return

        if python_library is not None:
            self._build_file.add_new_target(python_library)
            self._uncommitted_changes = True

        if python_test is not None:
            self._build_file.add_new_target(python_test)
            self._uncommitted_changes = True
        return

    def _parse_existing_python_targets(self):
        if self._this_pkg_build_file_path == "":
            raise ValueError(
                "programming error: pkg build file must be calculated before parsing existing Python targets"
            )

        with open(self._this_pkg_build_file_path, "r") as build_file:
            contents = build_file.read()

        contents_as_ast = ast.parse(contents)
        self._build_file = BUILDFile(contents_as_ast)
        return

    def __str__(self):
        return str(self._build_file)

    def write_to_build_file(self) -> str:
        if not self._uncommitted_changes:
            self._logger.debug(f"no changes made to {self._this_pkg_build_file_path}")
            return self._this_pkg_build_file_path

        dumped_ast = self._build_file.dump_ast()
        with open(self._this_pkg_build_file_path, "w") as build_file:
            build_file.write(dumped_ast)
            self._uncommitted_changes = False
            self._has_been_modified = True
        return self._this_pkg_build_file_path

    def has_uncommitted_changes(self) -> bool:
        return self._uncommitted_changes

    def path(self) -> str:
        return self._this_pkg_build_file_path

    @property
    def has_been_modified(self) -> bool:
        return self._has_been_modified
