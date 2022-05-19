import ast
import os
from collections import namedtuple

from imports.node_transformer import ToAbsoluteImports
from imports.py_import import Import, ImportType
from utils.mock_python_library_test_case import MockPythonLibraryTestCase


class TestToAbsoluteImportPaths(MockPythonLibraryTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.transformer = ToAbsoluteImports(os.getcwd())
        return

    def test_when_input_is_unexpected_ast_node_type(self):
        node = ast.Assign(targets="x", value="5")
        self.assertRaisesRegex(
            TypeError,
            "can only transform nodes of type Import and ImportFrom; got Assign",
            self.transformer.transform_all,
            [node],
        )
        return

    def test_import_nodes(self):
        node = ast.Import(
            names=[ast.alias(name="numpy.random", asname="rand"), ast.alias(name="os")]
        )
        self.assertEqual(
            [Import("numpy.random", ImportType.UNKNOWN), Import("os", ImportType.UNKNOWN)],
            self.transformer.transform_all([node]),
        )
        return

    def test_absolute_imports_in_import_from_nodes(self):
        SubTest = namedtuple("SubTest", ["name", "node", "expected_output"])
        subtests = [
            SubTest(
                name="import module from subpackage",
                node=ast.ImportFrom(
                    module=f"{self.test_dir}.test_subpackage",
                    level=0,
                    names=[ast.alias(name="test_module_1")],
                ),
                expected_output=[Import(f"{self.test_dir}.test_subpackage.test_module_1", ImportType.MODULE)],
            ),
            SubTest(
                name="import subpackage from package",
                node=ast.ImportFrom(
                    module=self.test_dir,
                    level=0,
                    names=[ast.alias(name="test_subpackage")],
                ),
                expected_output=[Import(f"{self.test_dir}.test_subpackage", ImportType.PACKAGE)],
            ),
            SubTest(
                name="import object from module",
                node=ast.ImportFrom(
                    module=f"{self.test_dir}.test_module_0",
                    level=0,
                    names=[ast.alias(name="Object")],
                ),
                expected_output=[Import(f"{self.test_dir}.test_module_0", ImportType.MODULE)],
            ),
        ]

        for subtest in subtests:
            with self.subTest(subtest.name):
                import_paths = self.transformer.transform_all([subtest.node])
                self.assertEqual(subtest.expected_output, import_paths)
        return

    def test_import_from_node_with_builtin_module(self):
        node = ast.ImportFrom(
            module="argparse",
            level=0,
            names=[ast.alias(name="ArgumentParser")],
        )

        self.assertEqual(
            [Import("argparse", ImportType.UNKNOWN)],
            self.transformer.transform_all([node]),
        )

        return

    def test_relative_imports_in_import_from_nodes(self):
        # TODO
        return

    def test_both_import_and_import_from_nodes(self):
        import_node = ast.Import(
            names=[ast.alias(name="numpy.random", asname="rand"), ast.alias(name="os")]
        )
        absolute_import_from_node = ast.ImportFrom(
            module=self.test_dir,
            level=0,
            names=[ast.alias(name="test_module_0"), ast.alias(name="test_subpackage")],
        )
        # TODO: add relative import
        # TODO: update assertion

        self.assertEqual(
            [
                Import("numpy.random", ImportType.UNKNOWN),
                Import("os", ImportType.UNKNOWN),
                Import(f"{self.test_dir}.test_module_0", ImportType.MODULE),
                Import(f"{self.test_dir}.test_subpackage", ImportType.PACKAGE),
            ],
            self.transformer.transform_all([import_node, absolute_import_from_node]),
        )
        return
