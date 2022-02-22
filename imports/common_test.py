from utils.mock_python_library_test_case import MockPythonLibraryTestCase
from imports.common import is_module, is_subpackage


class TestIsSubpackage(MockPythonLibraryTestCase):
    def test_is_subpackage_returns_true_for_dir(self):
        self.assertTrue(is_subpackage(self.test_dir))
        return

    def test_is_subpackage_returns_false_for_file(self):
        self.assertFalse(is_subpackage(self.subpackage_module))
        return

    def test_is_module_returns_true_for_file(self):
        self.assertTrue(is_module(self.subpackage_module))
        return

    def test_is_module_returns_false_for_dir(self):
        self.assertFalse(is_module(self.subpackage_dir))
        return
