import os
import re
from logging import INFO
from typing import Optional

from common.logger.logger import setup_logger


class NewPackageModuleFinder:
    __default_build_file_names__ = {"BUILD", "BUILD.plz"}

    def __init__(self, path_to_pkg: str, build_file_names: Optional[set[str]] = None):
        self._path_to_pkg = path_to_pkg
        self._build_file_names = (
            self.__default_build_file_names__
            if (build_file_names is None or len(build_file_names) == 0)
            else build_file_names
        )

        self._test_targets: set[str] = set()
        self._library_targets: set[str] = set()

        self._logger = setup_logger(__file__, INFO)
        return

    def find(self) -> None:
        self._validate()

        # Find all files in pkg dir.
        pkg_dir_files = {
            path for path in os.listdir(self._path_to_pkg)
            # filter out sub-directories
            if os.path.isfile(os.path.join(self._path_to_pkg, path))
        }

        # Find test srcs
        test_src_files = set(filter(lambda fn: fn.endswith("_test.py"), pkg_dir_files))

        # Find lib srcs
        non_test_src_files = pkg_dir_files - test_src_files
        lib_src_files = set(filter(lambda fn: re.match(r'.+\.pyi?$', fn), non_test_src_files))

        self._logger.info(
            f"In {self._path_to_pkg}, found {len(lib_src_files)} library sources "
            f"and {len(test_src_files)} test sources."
        )

        if len(test_src_files) == 0 and len(lib_src_files) == 0:
            return

        self._test_targets, self._library_targets = test_src_files, lib_src_files
        return

    def _validate(self):
        if not os.path.isdir(self._path_to_pkg):
            raise NotADirectoryError(self._path_to_pkg)

        for build_file_name in self._build_file_names:
            build_file_path = os.path.join(self._path_to_pkg, build_file_name)
            if os.path.isfile(build_file_path):
                self._logger.info(f"{self._path_to_pkg} already has a BUILD file")
                raise FileExistsError(build_file_path)

        return

    @property
    def test_targets(self) -> set[str]:
        return self._test_targets

    @property
    def library_targets(self) -> set[str]:
        return self._library_targets
