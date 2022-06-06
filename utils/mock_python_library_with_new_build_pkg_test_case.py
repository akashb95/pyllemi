import os

from utils.mock_python_library_test_case import MockPythonLibraryTestCase


class MockPythonLibraryWithNewBuildPkgTestCase(MockPythonLibraryTestCase):
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
