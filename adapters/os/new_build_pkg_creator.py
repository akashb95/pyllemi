import os.path
from typing import Optional

from adapters.os.new_package_module_finder import NewPackageModuleFinder
from domain.targets import python_target as target


class NewBuildPkgCreator:
    def __init__(self, path_to_pkg: str, build_file_names: Optional[set[str]] = None):
        self._path_to_pkg = path_to_pkg
        self._new_package_module_finder = NewPackageModuleFinder(path_to_pkg, build_file_names)
        return

    def infer_py_targets(self) -> tuple[Optional[target.PythonLibrary], Optional[target.PythonTest]]:
        """

        :return: 2-tuple of PythonLibrary and PythonTest targets (domain representation)
        """

        # Infer target names, and ensure funky chars are converted to underscores to be closer to snake case.
        # Note that this does not guarantee the target name is snake-case -- e.g. capital letters are not modified.
        lib_target_name = os.path.basename(self._path_to_pkg).replace("-", "_").replace(" ", "_")
        test_target_name = "_".join([lib_target_name, "test"])

        self._new_package_module_finder.find()
        library = self._infer_python_library(target_name=lib_target_name)
        test = self._infer_python_test(target_name=test_target_name)
        return library, test

    def _infer_python_library(self, *, target_name) -> Optional[target.PythonLibrary]:
        if len(self._new_package_module_finder.library_targets) == 0:
            return None
        return target.PythonLibrary(
            name=target_name,
            srcs=self._new_package_module_finder.library_targets,
            deps=set(),
        )

    def _infer_python_test(self, *, target_name) -> Optional[target.PythonTest]:
        if len(self._new_package_module_finder.test_targets) == 0:
            return None
        return target.PythonTest(
            name=target_name,
            srcs=self._new_package_module_finder.test_targets,
            deps=set(),
        )
