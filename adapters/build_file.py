import ast
import os
from dataclasses import dataclass

import astor


class Target:
    name: str
    deps: list[str]


@dataclass
class PythonLibrary(Target):
    srcs: list[str]


@dataclass
class PythonBinary(Target):
    srcs: list[str]


@dataclass
class BUILDFile:
    path_to_pkg: str
    build_file_name: str = "BUILD"

    def create(self):
        if not os.path.isdir(self.path_to_pkg):
            raise NotADirectoryError(self.path_to_pkg)

        build_file_path = os.path.join(self.path_to_pkg, self.build_file_name)
        if os.path.isfile(build_file_path):
            raise FileExistsError(build_file_path)

        return

    def update(self):
        if not os.path.isdir(self.path_to_pkg):
            raise NotADirectoryError(self.path_to_pkg)

        build_file_path = os.path.join(self.path_to_pkg, self.build_file_name)
        if not os.path.isfile(build_file_path):
            raise FileNotFoundError(build_file_path)

        root = astor.parse_file(build_file_path)
        # TODO: modify deps for code.
        return

    def _construct_build_file_contents(self) -> list[Target]:
        target_name = os.path.basename(self.path_to_pkg)

        pkg_dir_files = {
            path for path in os.listdir(self.path_to_pkg)
            # filter out sub-directories
            if os.path.isfile(os.path.join(self.path_to_pkg, path))
        }

        test_src_files = set(filter(lambda fn: fn.endswith("_test.py"), pkg_dir_files))
        src_files = pkg_dir_files - test_src_files

        target_definitions: list[Target] = []
        if len(src_files) > 0:
            target_definitions.append(
                PythonLibrary()
            )

        if len(test_src_files) > 0:
            pass

        # Round trip to AST for consistent formatting.
        # This makes the method easier to test.
        return ast.parse("\n\n".join(target_definitions) + "\n")
