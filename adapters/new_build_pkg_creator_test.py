from unittest import skip

from utils.mock_python_library_with_new_build_pkg_test_case import MockPythonLibraryWithNewBuildPkgTestCase


class MyTestCase(MockPythonLibraryWithNewBuildPkgTestCase):
    @skip("todo")
    def test_with_only_library_srcs(self):
        return

    @skip("todo")
    def test_with_only_test_srcs(self):
        return

    @skip("todo")
    def test_with_both_library_and_test_srcs(self):
        return

    @skip("todo")
    def test_with_no_eligible_srcs(self):
        return
