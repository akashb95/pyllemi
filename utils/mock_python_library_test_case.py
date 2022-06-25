import os
import uuid
from unittest import TestCase


class MockPythonLibraryTestCase(TestCase):
    def setUp(self) -> None:
        # Create package with a module, and a subpackage with another module.
        self.test_dir = f"test_pkg_{uuid.uuid4()}"
        self.plzconfig_file = os.path.join(self.test_dir, ".plzconfig")
        self.subpackage_dir = os.path.join(self.test_dir, "test_subpackage")
        self.package_build_file = os.path.join(self.test_dir, "BUILD")
        self.subpackage_build_file = os.path.join(self.subpackage_dir, "BUILD")
        self.package_module = os.path.join(self.test_dir, "test_module_0.py")
        self.subpackage_module = os.path.join(self.subpackage_dir, "test_module_1.py")

        if os.path.exists(self.test_dir):
            raise FileExistsError(f"cannot create {self.test_dir} for test setup: path already exists")
        os.makedirs(self.test_dir)

        if os.path.exists(self.subpackage_dir):
            raise FileExistsError(f"cannot create {self.subpackage_dir} for test setup: path already exists")
        os.makedirs(self.subpackage_dir)

        with open(self.plzconfig_file, "w") as f:
            f.write(f"# TEST: {self.test_dir}")

        with open(self.package_build_file, "w") as f:
            f.write(f"# TEST: {self.test_dir}")

        with open(self.subpackage_build_file, "w") as f:
            f.write("""python_test(name="test_subpackage", srcs=["test_module_1.py"])""")

        with open(self.package_module, "w") as f:
            f.write("x = 5")

        with open(self.subpackage_module, "w") as f:
            f.write("y = 10")

        self.test_wd = os.path.abspath(os.getcwd())

        self.files_to_delete: list[str] = [
            self.package_module,
            self.subpackage_module,
            self.plzconfig_file,
            self.package_build_file,
            self.subpackage_build_file,
        ]
        # The order matters - cannot delete a dir that is not empty.
        # The deletion will be carried out in the tearDown.
        self.dirs_to_delete: list[str] = [self.subpackage_dir, self.test_dir]
        return

    def tearDown(self) -> None:
        for file in self.files_to_delete:
            try:
                os.unlink(file)
            except FileNotFoundError:
                pass
        for d in self.dirs_to_delete:
            os.rmdir(d)
        return
