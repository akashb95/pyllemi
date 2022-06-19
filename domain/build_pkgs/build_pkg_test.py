import ast
from unittest import mock

from domain.build_pkgs.build_pkg import BUILDPkg
from domain.targets.python_target import PythonLibrary, PythonTest
from utils.mock_python_library_with_new_build_pkg_test_case import (
    MockPythonLibraryTestCase,
    MockPythonLibraryWithNewBuildPkgTestCase,
)


class TestBuildPkgWithNewBuildPkg(MockPythonLibraryWithNewBuildPkgTestCase):
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("domain.build_pkgs.build_pkg.NewBuildPkgCreator", autospec=True)
    @mock.patch("domain.build_pkgs.build_pkg.BUILDFile", autospec=True)
    def test_initialise(
        self,
        mock_build_file: mock.MagicMock,
        mock_new_build_pkg_creator: mock.MagicMock,
        mock_file_open: mock.MagicMock,
    ):
        mock_new_build_pkg_creator_instance: mock.MagicMock = mock_new_build_pkg_creator.return_value
        mock_new_build_pkg_creator_instance.infer_py_targets.return_value = (
            PythonLibrary(name="name", srcs={"module.py", "stub_module.pyi"}, deps=set()),
            PythonTest(name="name_test", srcs={"module_test.py"}, deps=set()),
        )
        mock_build_file_instance: mock.MagicMock = mock_build_file.return_value
        mock_dumped_ast = """
        python_library(name="name", srcs=["module.py", "stub_module.pyi"], deps=[]),
        python_test(name="name", srcs=["module_test.py"], deps=[]),
        """
        mock_build_file_instance.dump_ast.return_value = mock_dumped_ast

        BUILDPkg(self.new_pkg_path, frozenset({"BUILD"}))

        mock_new_build_pkg_creator.assert_called_once_with(self.new_pkg_path, frozenset({"BUILD"}))
        mock_new_build_pkg_creator_instance.infer_py_targets.assert_called_once()
        self.assertEqual(2, mock_build_file_instance.add_new_target.call_count)
        mock_file_open.return_value.write.assert_called_once_with(mock_dumped_ast)

        return

    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("domain.build_pkgs.build_pkg.NewBuildPkgCreator", autospec=True)
    @mock.patch("domain.build_pkgs.build_pkg.BUILDFile", autospec=True)
    def test_resolve_deps_for_targets(
        self,
        mock_build_file: mock.MagicMock,
        mock_new_build_pkg_creator: mock.MagicMock,
        mock_file_open: mock.MagicMock,
    ):
        mock_new_build_pkg_creator_instance: mock.MagicMock = mock_new_build_pkg_creator.return_value
        mock_new_build_pkg_creator_instance.infer_py_targets.return_value = (
            mock_python_lib := PythonLibrary(name="name", srcs={"module.py", "stub_module.pyi"}, deps=set()),
            None,
        )
        mock_build_file_instance: mock.MagicMock = mock_build_file.return_value
        mock_dumped_ast = """python_library(name="name", srcs=["module.py", "stub_module.pyi"], deps=[])"""
        mock_build_file_instance.dump_ast.return_value = mock_dumped_ast

        build_pkg = BUILDPkg(self.new_pkg_path, frozenset({"BUILD"}))

        mock_new_build_pkg_creator.assert_called_once_with(self.new_pkg_path, frozenset({"BUILD"}))
        mock_new_build_pkg_creator_instance.infer_py_targets.assert_called_once()
        mock_build_file_instance.add_new_target.assert_called_once_with(mock_python_lib)
        mock_file_open.return_value.write.assert_called_once_with(mock_dumped_ast)

        mock_node_to_be_modified: ast.Call = ast.parse(mock_dumped_ast).body[0].value
        mock_build_file_instance.get_existing_ast_python_build_rules.return_value = [mock_node_to_be_modified]
        build_pkg.resolve_deps_for_targets(lambda plz_target, srcs: {":dep"})
        mock_build_file_instance.register_modified_build_rule_to_python_target.assert_called_once_with(
            mock_node_to_be_modified,
            PythonLibrary(name="name", srcs={"module.py", "stub_module.pyi"}, deps={":dep"}),
        )
        self.assertTrue(build_pkg._uncommitted_changes)
        return


class TestBuildPkgWithExistingBuildFile(MockPythonLibraryTestCase):
    @mock.patch("domain.build_pkgs.build_pkg.NewBuildPkgCreator", autospec=True)
    @mock.patch("domain.build_pkgs.build_pkg.BUILDFile", autospec=True)
    def test_initialise(
        self,
        mock_build_file: mock.MagicMock,
        mock_new_build_pkg_creator: mock.MagicMock,
        # mock_file_open: mock.MagicMock,
    ):
        mock_new_build_pkg_creator_instance: mock.MagicMock = mock_new_build_pkg_creator.return_value
        mock_new_build_pkg_creator_instance.infer_py_targets.assert_not_called()
        mock_build_file_instance: mock.MagicMock = mock_build_file.return_value

        build_pkg = BUILDPkg(self.subpackage_dir, frozenset({"BUILD"}))

        mock_new_build_pkg_creator.assert_called_once_with(self.subpackage_dir, frozenset({"BUILD"}))
        mock_build_file_instance.add_new_target.assert_not_called()
        mock_build_file_instance.dump_ast.assert_not_called()

        mock_dumped_ast = (
            """python_test(name="test_subpackage", srcs=["test_module_0.py", "test_module_1.py"], deps=[])"""
        )
        mock_node_to_be_modified: ast.Call = ast.parse(mock_dumped_ast).body[0].value
        mock_build_file_instance.get_existing_ast_python_build_rules.return_value = [mock_node_to_be_modified]
        build_pkg.resolve_deps_for_targets(lambda plz_target, srcs: {":dep"})
        mock_build_file_instance.register_modified_build_rule_to_python_target.assert_called_once_with(
            mock_node_to_be_modified,
            PythonTest(
                name="test_subpackage",
                srcs={"test_module_0.py", "test_module_1.py"},
                deps={":dep"},
            ),
        )
        self.assertTrue(build_pkg._uncommitted_changes)
        return
