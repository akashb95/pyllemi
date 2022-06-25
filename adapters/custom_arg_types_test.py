import argparse
import os
import uuid
from unittest import TestCase

from adapters.custom_arg_types import existing_file_arg_type, existing_dir_arg_type


class TestExistingFileArgType(TestCase):
    def setUp(self) -> None:
        self.test_dir_path = os.path.abspath(f"test_dir_{uuid.uuid4()}")
        if os.path.exists(self.test_dir_path):
            raise FileExistsError(f"Cannot create dir because path already exists: {self.test_dir_path}")
        os.makedirs(self.test_dir_path)

        with open(os.path.join(self.test_dir_path, "module.py"), "w") as f:
            f.write(f"# TEST {self.__class__.__name__}")
            f.write("import numpy")
        return

    def tearDown(self) -> None:
        # Delete test files and dir.
        for file in os.listdir(self.test_dir_path):
            os.unlink(os.path.join(self.test_dir_path, file))
        os.rmdir(self.test_dir_path)
        return

    def test_existing_file_arg_type(self):
        test_path = os.path.join(self.test_dir_path, "module.py")
        self.assertEqual(test_path, existing_file_arg_type(test_path))
        return

    def test_when_path_is_a_directory(self):
        self.assertRaisesRegex(
            argparse.ArgumentTypeError,
            f"expected {self.test_dir_path} to be a file, but is a dir instead",
            existing_file_arg_type,
            self.test_dir_path,
        )
        return

    def test_when_path_does_not_exist(self):
        non_existent_path = os.path.join(self.test_dir_path, "does_not_exist")
        self.assertRaisesRegex(
            argparse.ArgumentTypeError,
            f"could not find {non_existent_path}",
            existing_file_arg_type,
            non_existent_path,
        )
        return


class TestExistingDirArgType(TestCase):
    def setUp(self) -> None:
        self.test_dir_path = os.path.abspath(f"test_dir_{uuid.uuid4()}")
        if os.path.exists(self.test_dir_path):
            raise FileExistsError(f"Cannot create dir because path already exists: {self.test_dir_path}")
        os.makedirs(self.test_dir_path)

        with open(os.path.join(self.test_dir_path, "module.py"), "w") as f:
            f.write(f"# TEST {self.__class__.__name__}")
            f.write("import numpy")
        return

    def tearDown(self) -> None:
        # Delete test files and dir.
        for file in os.listdir(self.test_dir_path):
            os.unlink(os.path.join(self.test_dir_path, file))
        os.rmdir(self.test_dir_path)
        return

    def test_with_dir(self):
        test_path = self.test_dir_path
        self.assertEqual(test_path, existing_dir_arg_type(test_path))
        return

    def test_with_file(self):
        test_path = os.path.join(self.test_dir_path, "module.py")
        self.assertRaisesRegex(
            argparse.ArgumentTypeError,
            f"expected {test_path} to be a dir, but is a file instead",
            existing_dir_arg_type,
            test_path,
        )
        return

    def test_with_invalid_path(self):
        test_path = "potato"
        self.assertRaisesRegex(
            argparse.ArgumentTypeError,
            f"could not find {test_path}",
            existing_dir_arg_type,
            test_path,
        )
        return
