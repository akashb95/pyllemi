import os
from unittest import TestCase

from utils.mock_python_library_test_case import MockPythonLibraryTestCase
from imports.py_import import Import, ImportType, resolve_import_type, to_whatinputs_input


class TestResolveImportType(MockPythonLibraryTestCase):
    def test_import_of_module(self):
        py_import = f"{self.test_dir}.test_module_0"
        self.assertEqual(
            ImportType.MODULE,
            resolve_import_type(py_import, "does.not.matter"),
        )
        return

    def test_builtin_module_import(self):
        self.assertEqual(
            ImportType.UNKNOWN,
            resolve_import_type("os.path", "does.not.matter"),
        )
        return

    def test_import_of_package(self):
        py_import = f"{self.test_dir}.test_subpackage"
        self.assertEqual(
            ImportType.PACKAGE,
            resolve_import_type(py_import, "does.not.matter"),
        )
        return


class TestToWhatInputsInput(TestCase):
    def test_module(self):
        import_ = Import("test.module", ImportType.MODULE)
        self.assertEqual(
            [os.path.join("test", "module.py")],
            to_whatinputs_input(import_),
        )
        return

    def test_package(self):
        import_ = Import("test.package", ImportType.PACKAGE)
        self.assertEqual(
            [os.path.join("test", "package", "**", "*.py"), os.path.join("test", "package", "**", "*.pyi")],
            to_whatinputs_input(import_),
        )
        return

    def test_unknown_import_type(self):
        import_ = Import("test", ImportType.UNKNOWN)
        self.assertIsNone(to_whatinputs_input(import_))
        return

    def test_stub(self):
        import_ = Import("test.stub", ImportType.STUB)
        self.assertEqual(
            [os.path.join("test", "stub.pyi")],
            to_whatinputs_input(import_),
        )
        return
