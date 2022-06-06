import os

from adapters.new_package_module_finder import NewPackageModuleFinder
from utils.mock_python_library_with_new_build_pkg_test_case import MockPythonLibraryWithNewBuildPkgTestCase


class TestNewPackageModuleFinder(MockPythonLibraryWithNewBuildPkgTestCase):
    def test_errors_if_build_file_exists(self):
        new_package_module_finder = NewPackageModuleFinder(self.test_dir)
        self.assertRaisesRegex(
            FileExistsError,
            f"{os.path.join(self.test_dir, 'BUILD')}",
            new_package_module_finder.find,
        )
        return

    def test_errors_if_pkg_dir_does_not_exist(self):
        new_package_module_finder = NewPackageModuleFinder("doesnt-exist")
        self.assertRaisesRegex(
            NotADirectoryError,
            "doesnt-exist",
            new_package_module_finder.find,
        )
        return

    def test_finds_lib_srcs(self):
        new_package_module_finder = NewPackageModuleFinder(self.subpackage_dir)
        new_package_module_finder.find()

        self.assertEqual(0, len(new_package_module_finder.test_targets))
        self.assertEqual(1, len(new_package_module_finder.library_targets))
        self.assertEqual({"test_module_1.py"}, new_package_module_finder.library_targets)
        return

    def test_finds_test_srcs(self):
        new_package_module_finder = NewPackageModuleFinder(self.new_pkg_path)
        # Delete non-test sources
        os.unlink(self.new_pkg_lib_src_0)
        os.unlink(self.new_pkg_lib_src_1)

        new_package_module_finder.find()

        self.assertEqual(1, len(new_package_module_finder.test_targets))
        self.assertEqual(0, len(new_package_module_finder.library_targets))
        self.assertEqual({"module_test.py"}, new_package_module_finder.test_targets)
        return

    def test_finds_both_lib_and_test_srcs(self):
        new_package_module_finder = NewPackageModuleFinder(self.new_pkg_path)
        new_package_module_finder.find()

        self.assertEqual(1, len(new_package_module_finder.test_targets))
        self.assertEqual(2, len(new_package_module_finder.library_targets))
        self.assertEqual({"module_test.py"}, new_package_module_finder.test_targets)
        self.assertEqual({"module.py", "stub_module.pyi"}, new_package_module_finder.library_targets)
        return
