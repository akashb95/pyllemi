import os

from adapters.new_build_pkg_creator import NewBuildPkgCreator
from targets import target
from utils.mock_python_library_with_new_build_pkg_test_case import MockPythonLibraryWithNewBuildPkgTestCase


class MyTestCase(MockPythonLibraryWithNewBuildPkgTestCase):
    def test_with_only_library_srcs(self):
        new_build_pkg_creator = NewBuildPkgCreator(self.new_pkg_path)
        os.unlink(self.new_pkg_test_src)
        library, test = new_build_pkg_creator.infer_py_targets()
        self.assertIsNone(test)
        self.assertEqual(
            target.PythonLibrary(name="new_pkg", srcs={"module.py", "stub_module.pyi"}, deps=set(), other_kwargs={}),
            library,
        )
        return

    def test_with_only_test_srcs(self):
        new_build_pkg_creator = NewBuildPkgCreator(self.new_pkg_path)
        os.unlink(self.new_pkg_lib_src_0)
        os.unlink(self.new_pkg_lib_src_1)

        library, test = new_build_pkg_creator.infer_py_targets()
        self.assertIsNone(library)
        self.assertEqual(
            target.PythonTest(name="new_pkg_test", srcs={"module_test.py"}, deps=set(), other_kwargs={}),
            test,
        )
        return

    def test_with_both_library_and_test_srcs(self):
        new_build_pkg_creator = NewBuildPkgCreator(self.new_pkg_path)

        library, test = new_build_pkg_creator.infer_py_targets()
        self.assertEqual(
            target.PythonLibrary(name="new_pkg", srcs={"module.py", "stub_module.pyi"}, deps=set(), other_kwargs={}),
            library,
        )
        self.assertEqual(
            target.PythonTest(name="new_pkg_test", srcs={"module_test.py"}, deps=set(), other_kwargs={}),
            test,
        )
        return

    def test_with_no_eligible_srcs(self):
        new_build_pkg_creator = NewBuildPkgCreator(self.new_pkg_path)
        os.unlink(self.new_pkg_lib_src_0)
        os.unlink(self.new_pkg_lib_src_1)
        os.unlink(self.new_pkg_test_src)

        library, test = new_build_pkg_creator.infer_py_targets()
        self.assertIsNone(library)
        self.assertIsNone(test)
        return
