import os
from unittest import TestCase

from utils.mock_python_library_test_case import MockPythonLibraryTestCase
from converters.paths import (
    convert_py_import_path_to_os_path,
    convert_os_path_to_import_path,
)


class TestConvertPyImportPathToOSPath(MockPythonLibraryTestCase):
    def test_import_of_module(self):
        py_import = f"{self.test_dir}.test_module_0"
        converted = convert_py_import_path_to_os_path(py_import)
        self.assertEqual(os.path.abspath(self.package_module), converted)
        return

    def test_import_of_module_that_has_no_fspath(self):
        py_import = "argparse.ArgumentParser"
        converted = convert_py_import_path_to_os_path(py_import)
        self.assertIsNone(converted)
        return

    def test_import_of_package(self):
        py_import = f"{self.test_dir}.test_subpackage"
        converted = convert_py_import_path_to_os_path(py_import)
        self.assertEqual(os.path.abspath(self.subpackage_dir), converted)
        return


class TestConvertOSPathToPyImportPath(TestCase):
    def test_dirname(self):
        test_pkg_path = os.path.join("test", "pkg")
        converted = convert_os_path_to_import_path(test_pkg_path)
        self.assertEqual("test.pkg", converted)
        return

    def test_filename(self):
        test_module_path = os.path.join("test", "pkg", "module.py")
        converted = convert_os_path_to_import_path(test_module_path)
        self.assertEqual("test.pkg.module", converted)
        return

    def test_with_project_root(self):
        test_module_path = os.path.abspath(
            os.path.join("root", "project_root", "test", "pkg", "module.py")
        )
        converted = convert_os_path_to_import_path(
            test_module_path, os.path.abspath(os.path.join("root", "project_root"))
        )
        self.assertEqual("test.pkg.module", converted)
        return
