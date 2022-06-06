import re
from dataclasses import dataclass

from common.logger.logger import setup_logger

@dataclass
class NewPackageModuleFinder:
    path_to_pkg: str
    build_file_names: set[str] = {"BUILD"}

    _test_targets: set[str] = set()
    _library_targets: set[str] = set()
    _logger = setup_logger(__file__)

    def find(self) -> bool:
        self._validate()

        # Find all files in pkg dir.
        pkg_dir_files = {
            path for path in os.listdir(self.path_to_pkg)
            # filter out sub-directories
            if os.path.isfile(os.path.join(self.path_to_pkg, path))
        }

        # Find test srcs
        test_src_files = set(filter(lambda fn: fn.endswith("_test.py"), pkg_dir_files))
        non_test_src_files = pkg_dir_files - test_src_files

        lib_src_files = set(filter(lambda fn: re.match(r'*\.pyi?$'), non_test_src_files))
        return

    def _validate(self):
        if not os.path.isdir(self.path_to_pkg):
            raise NotADirectoryError(self.path_to_pkg)

        for build_file_name in build_file_name:
            build_file_path = os.path.join(self.path_to_pkg, self.build_file_name)
            if os.path.isfile(build_file_path):
                self._logger.info(f"{self.path_to_pkg} already has a BUILD file")
                raise FileExistsError(build_file_path)

        return
    
    @property
    def test_targets(self) -> set[str]:
        return self._test_targets

    @property
    def library_targets(self) -> set[str]:
        return self._library_targets
