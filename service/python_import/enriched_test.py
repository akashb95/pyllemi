import os

from domain.python_import import enriched as enriched_import
from service.python_import.enriched import resolve_import_type, to_whatinputs_input
from utils.mock_python_library_test_case import MockPythonLibraryTestCase


class TestResolveType(MockPythonLibraryTestCase):
    def test_import_of_module(self):
        py_import = f"{self.test_dir}.test_module_0"
        self.assertEqual(
            enriched_import.Type.MODULE,
            resolve_import_type(py_import, "does.not.matter"),
        )
        return

    def test_builtin_module_import(self):
        self.assertEqual(
            enriched_import.Type.UNKNOWN,
            resolve_import_type("os.path", "does.not.matter"),
        )
        return

    def test_import_of_package(self):
        py_import = f"{self.test_dir}.test_subpackage"
        self.assertEqual(
            enriched_import.Type.PACKAGE,
            resolve_import_type(py_import, "does.not.matter"),
        )
        return


class TestToWhatInputsInput(MockPythonLibraryTestCase):
    def test_module(self):
        import_ = enriched_import.Import("test.module", enriched_import.Type.MODULE)
        self.assertEqual(
            [os.path.join("test", "module.py")],
            to_whatinputs_input(import_),
        )
        return

    def test_package(self):
        import_ = enriched_import.Import(self.subpackage_dir, enriched_import.Type.PACKAGE)
        self.assertEqual(
            [self.subpackage_module],
            to_whatinputs_input(import_),
        )
        return

    def test_unknown_import_type(self):
        import_ = enriched_import.Import("test", enriched_import.Type.UNKNOWN)
        self.assertIsNone(to_whatinputs_input(import_))
        return

    def test_stub(self):
        import_ = enriched_import.Import("test.stub", enriched_import.Type.STUB)
        self.assertEqual(
            [os.path.join("test", "stub.pyi")],
            to_whatinputs_input(import_),
        )
        return
