import ast
import os
from collections import namedtuple

from imports.enricher import ToEnrichedImports
from imports.enriched_import import EnrichedImport, ImportType
from utils.mock_python_library_test_case import MockPythonLibraryTestCase


class TestToImportPaths(MockPythonLibraryTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.transformer = ToEnrichedImports(os.getcwd(), "third_party.python3")
        return

    def test_when_input_is_unexpected_ast_node_type(self):
        node = ast.Assign(targets="x", value="5")
        self.assertRaisesRegex(
            TypeError,
            "can only transform nodes of type Import and ImportFrom; got Assign",
            self.transformer.convert_all,
            [node],
        )
        return

    def test_import_nodes(self):
        node = ast.Import(
            names=[ast.alias(name="numpy.random", asname="rand"), ast.alias(name="os")]
        )
        self.assertEqual(
            [EnrichedImport("numpy.random", ImportType.UNKNOWN), EnrichedImport("os", ImportType.UNKNOWN)],
            self.transformer.convert_all([node]),
        )
        return

    def test_import_node_when_specifying_moduledir_in_third_party_import(self):
        node = ast.Import(
            names=[ast.alias(name="third_party.python3.numpy.random", asname="rand")],
        )

        self.assertEqual(
            [EnrichedImport("numpy", ImportType.THIRD_PARTY_MODULE)],
            self.transformer.convert_all([node]),
        )
        return

    def test_import_from_node_when_specifying_moduledir_in_third_party_import(self):
        node = ast.ImportFrom(
            module="third_party.python3.numpy.random",
            level=0,
            names=[ast.alias(name="Object")],
        )

        self.assertEqual(
            [EnrichedImport("numpy", ImportType.THIRD_PARTY_MODULE)],
            self.transformer.convert_all([node]),
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
                expected_output=[EnrichedImport(f"{self.test_dir}.test_subpackage.test_module_1", ImportType.MODULE)],
            ),
            SubTest(
                name="import subpackage from package",
                node=ast.ImportFrom(
                    module=self.test_dir,
                    level=0,
                    names=[ast.alias(name="test_subpackage")],
                ),
                expected_output=[EnrichedImport(f"{self.test_dir}.test_subpackage", ImportType.PACKAGE)],
            ),
            SubTest(
                name="import object from module",
                node=ast.ImportFrom(
                    module=f"{self.test_dir}.test_module_0",
                    level=0,
                    names=[ast.alias(name="Object")],
                ),
                expected_output=[EnrichedImport(f"{self.test_dir}.test_module_0", ImportType.MODULE)],
            ),
        ]

        for subtest in subtests:
            with self.subTest(subtest.name):
                import_paths = self.transformer.convert_all([subtest.node])
                self.assertEqual(subtest.expected_output, import_paths)
        return

    def test_import_from_node_with_builtin_module(self):
        node = ast.ImportFrom(
            module="argparse",
            level=0,
            names=[ast.alias(name="ArgumentParser")],
        )

        self.assertEqual(
            [EnrichedImport("argparse", ImportType.UNKNOWN)],
            self.transformer.convert_all([node]),
        )

        return

    def test_relative_import_from_module_without_parent_pkg_errors(self):
        node = ast.ImportFrom(
            module="does.not.matter",
            level=1,
            names=[ast.alias(name="x")]
        )

        self.assertRaisesRegex(
            ImportError,
            "attempted relative import with no known parent package.*",
            self.transformer.convert_all,
            [node],
            pyfile_path="main.py",
        )

        return

    def test_relative_import_when_moving_out_of_root_dir_errors(self):
        with self.subTest("with module specified"):
            node = ast.ImportFrom(
                module="does.not.matter",
                level=4,
                names=[ast.alias(name="x")]
            )

            self.assertRaisesRegex(
                ImportError,
                "attempted relative import beyond top-level package",
                self.transformer.convert_all,
                [node],
                pyfile_path=os.path.join("new_subpkg", "module.py")
            )

        with self.subTest("with no module specified"):
            node = ast.ImportFrom(
                module=None,
                level=4,
                names=[ast.alias(name="x")]
            )

            self.assertRaisesRegex(
                ImportError,
                "attempted relative import beyond top-level package",
                self.transformer.convert_all,
                [node],
                pyfile_path=os.path.join("new_subpkg", "module.py")
            )

        return

    def test_relative_import_with_module(self):
        """
        Imports of the form:
        * `from ..pkg.subpkg import Object`
        * `from ..pkg import subpkg`
        """

        with self.subTest("when importing module"):
            node = ast.ImportFrom(
                module=f"{self.subpackage_dir.replace(os.path.sep, '.')}.test_module_1",
                level=2,
                names=[ast.alias(name="x")],
            )

            self.assertEqual(
                [EnrichedImport(f"{os.path.splitext(self.subpackage_module)[0].replace(os.path.sep, '.')}", ImportType.MODULE)],
                self.transformer.convert_all([node], pyfile_path=os.path.join("new_pkg", "module.py")),
            )

        with self.subTest("when module defined as a name"):
            node = ast.ImportFrom(
                module=self.subpackage_dir.replace(os.path.sep, '.'),
                level=2,
                names=[ast.alias(name="test_module_1")],
            )

            self.assertEqual(
                [EnrichedImport(f"{os.path.splitext(self.subpackage_module)[0].replace(os.path.sep, '.')}", ImportType.MODULE)],
                self.transformer.convert_all([node], pyfile_path=os.path.join("new_subpkg", "module.py")),
            )

        return

    def test_relative_imports_without_module(self):
        """
        Imports of the form:
        * `from .. import module`
        * `from ... import Object`
        """

        node = ast.ImportFrom(
            module=None,
            level=2,
            names=[ast.alias(name=f"{self.subpackage_dir.replace(os.path.sep, '.')}.test_module_1")],
        )

        self.assertEqual(
            [EnrichedImport(f"{os.path.splitext(self.subpackage_module)[0].replace(os.path.sep, '.')}", ImportType.MODULE)],
            self.transformer.convert_all([node], pyfile_path=os.path.join("new_subpkg", "module.py")),
        )

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
                EnrichedImport("numpy.random", ImportType.UNKNOWN),
                EnrichedImport("os", ImportType.UNKNOWN),
                EnrichedImport(f"{self.test_dir}.test_module_0", ImportType.MODULE),
                EnrichedImport(f"{self.test_dir}.test_subpackage", ImportType.PACKAGE),
            ],
            self.transformer.convert_all([import_node, absolute_import_from_node]),
        )
        return
