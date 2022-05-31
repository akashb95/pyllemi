import ast
import os
from typing import List, Union

import astor

from adapters.build_file import BUILDFile
from utils.mock_python_library_test_case import MockPythonLibraryTestCase


class TestBUILDFile(MockPythonLibraryTestCase):
    def setUp(self):
        super().setUp()

        self.new_subpackage_path = os.path.join(self.test_dir, "new_subpkg")
        if os.path.exists(self.new_subpackage_path):
            raise FileExistsError(
                f"cannot create {self.subpackage_dir} for test setup: path already exists"
            )
        os.makedirs(self.new_subpackage_path)

        self.dirs_to_delete = [self.new_subpackage_path] + self.dirs_to_delete

        for module_file_name in ("module_0.py", "module_1.py", "module_0_test.py", "e2e_test.py"):
            with open(pyfile_path := os.path.join(self.new_subpackage_path, module_file_name), "w") as pyfile:
                pyfile.write("x = 5")
            self.files_to_delete.append(pyfile_path)

        self.test_build_file_adapter = BUILDFile(self.new_subpackage_path)
        return

    def test_create(self):
        pass

    def test_construct_build_file_contents(self):
        expected_target_definitions = ast.parse("""
python_library(
    name = "new_subpkg",
    srcs = ["module_0.py", "module_1.py"],
    deps = [],
)

python_test(
    name = "new_subpkg_test",
    srcs = ["module_0_test.py", "e2e_test.py"],
    deps = [":new_subpkg"],
)
 """)
        target_definitions = self.test_build_file_adapter._construct_build_file_contents()
        # self.assertEqual(expected_target_definitions, target_definitions)
        self.assertTrue(compare_ast(ast.parse(expected_target_definitions), ast.parse(target_definitions)))
        return


def compare_ast(node1: Union[ast.expr, List[ast.expr]], node2: Union[ast.expr, List[ast.expr]]) -> bool:
    if type(node1) is not type(node2):
        return False

    if isinstance(node1, ast.Module):
        return compare_ast(node1.body, node2.body)

    if isinstance(node1, ast.AST):
        for k, v in vars(node1).items():
            if k in ("lineno", "col_offset", "ctx"):
                continue
            if not compare_ast(v, getattr(node2, k)):
                return False
        return True

    elif isinstance(node1, list) and isinstance(node2, list):
        return all([compare_ast(n1, n2) for n1, n2 in zip(node1, node2)])
    else:
        return node1 == node2
