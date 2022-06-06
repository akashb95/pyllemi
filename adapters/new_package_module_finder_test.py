import os

from adapters.new_package_module_finder import NewPackageModuleFinder
from utils.mock_python_library_test_case import MockPythonLibraryTestCase


class TestNewPackageModuleFinder(MockPythonLibraryTestCase):
    def setUp(self):
        super().setUp()

        self.new_pkg_path = os.path.join(self.test_dir, "new_pkg")
        self.new_pkg_lib_src_0 = os.path.join(self.new_pkg_path, "module.py")
        self.new_pkg_lib_src_1 = os.path.join(self.new_pkg_path, "stub_module.pyi")
        self.new_pkg_test_src = os.path.join(self.new_pkg_path, "module_test.py")

        if os.path.exists(self.new_pkg_path):
            raise IsADirectoryError(
                f"cannot create {self.new_pkg_path} for test setup: path already exists"
            )
        os.makedirs(self.new_pkg_path)

        if os.path.exists(self.new_pkg_lib_src_0):
            raise FileNotFoundError(
                f"cannot create {self.new_pkg_lib_src_0} for test setup: path already exists"
            )
        with open(self.new_pkg_lib_src_0, "w") as f:
            f.write("x = 10")

        if os.path.exists(self.new_pkg_lib_src_1):
            raise FileNotFoundError(
                f"cannot create {self.new_pkg_lib_src_1} for test setup: path already exists"
            )
        with open(self.new_pkg_lib_src_1, "w") as f:
            f.write("x = 1")

        if os.path.exists(self.new_pkg_test_src):
            raise FileNotFoundError(
                f"cannot create {self.new_pkg_test_src} for test setup: path already exists"
            )
        with open(self.new_pkg_test_src, "w") as f:
            f.write("x = 'test'")

        self.files_to_delete.extend([self.new_pkg_lib_src_0, self.new_pkg_lib_src_1, self.new_pkg_test_src])
        self.dirs_to_delete = [self.new_pkg_path] + self.dirs_to_delete

        return

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
