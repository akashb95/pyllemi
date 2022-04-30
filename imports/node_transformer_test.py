import ast
import os
from collections import namedtuple

from utils.mock_python_library_test_case import MockPythonLibraryTestCase
from imports.node_transformer import ToAbsoluteImportPaths


class TestToAbsoluteImportPaths(MockPythonLibraryTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.transformer = ToAbsoluteImportPaths(os.getcwd())
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
        self.assertEqual(["numpy.random", "os"], self.transformer.transform_all([node]))
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
                expected_output=[f"{self.test_dir}.test_subpackage.test_module_1"],
            ),
            SubTest(
                name="import subpackage from package",
                node=ast.ImportFrom(
                    module=self.test_dir,
                    level=0,
                    names=[ast.alias(name="test_subpackage")],
                ),
                expected_output=[f"{self.test_dir}.test_subpackage"],
            ),
            SubTest(
                name="import object from module",
                node=ast.ImportFrom(
                    module=self.test_dir,
                    level=0,
                    names=[ast.alias(name="test_module_0")],
                ),
                expected_output=[f"{self.test_dir}.test_module_0"],
            ),
        ]

        for subtest in subtests:
            with self.subTest(subtest.name):
                import_paths = self.transformer.transform_all([subtest.node])
                self.assertEqual(subtest.expected_output, import_paths)
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
                "numpy.random",
                "os",
                f"{self.test_dir}.test_module_0",
                f"{self.test_dir}.test_subpackage",
            ],
            self.transformer.transform_all([import_node, absolute_import_from_node]),
        )
        return
