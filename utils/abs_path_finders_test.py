import os
import uuid
from unittest import TestCase

from utils.mock_python_library_test_case import MockPythonLibraryTestCase
from utils.abs_path_finders import (
    _to_cwd_with_any_files,
    to_closest_build_pkg_dir,
    to_project_root,
)


class TestAbsPathFinders(MockPythonLibraryTestCase):
    def setUp(self) -> None:
        self.test_wd = os.path.abspath(os.getcwd())
        super().setUp()
        return

    def tearDown(self) -> None:
        os.chdir(self.test_wd)
        super().tearDown()
        return

    def test_project_root_finder(self):
        os.chdir(os.path.abspath(self.subpackage_dir))
        expected_project_root = os.path.join(self.test_wd, self.test_dir)
        project_root = to_project_root()
        self.assertEqual(
            expected_project_root,
            project_root,
        )
        return

    def test_build_pkg_finder(self):
        os.chdir(os.path.abspath(self.subpackage_dir))
        expected_build_pkg_dir = os.path.join(self.test_wd, self.test_dir)
        build_pkg_dir = to_closest_build_pkg_dir({"BUILD", "BUILD.plz"})
        self.assertEqual(expected_build_pkg_dir, build_pkg_dir)
        return


class TestFinderRaisesErr(TestCase):
    # Happy path tested by callers of this hidden function.
    def test_when_file_not_found(self):
        self.assertRaisesRegex(
            FileNotFoundError,
            "could not find Please project root.*",
            _to_cwd_with_any_files,
            {str(uuid.uuid4())},
        )
        return
