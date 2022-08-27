import ast
import os
import sys
from unittest import mock, TestCase

from adapters.plz_cli.query import WhatInputsResult
from domain.plz.target.target import Target
from domain.python_import import enriched as enriched_import
from service.dependency.resolver import DependencyResolver, convert_os_path_to_import_path


class TestDependencyResolver(TestCase):
    def setUp(self) -> None:
        self.mock_nodes_collector = mock.MagicMock()
        self.mock_enricher = mock.MagicMock()
        return

    @mock.patch("builtins.open", new_callable=mock.mock_open(read_data="import colorama"))
    def test_resolve_deps_for_srcs_with_third_party_module(self, mock_file_open: mock.MagicMock):
        self.mock_nodes_collector.collate.return_value = [
            mock_import_node := ast.Import(names=[ast.Name(name="colorama")])
        ]
        mock_file_open.return_value.__enter__.return_value.read.return_value = "import colorama"
        self.mock_enricher.convert.return_value = [
            [enriched_import.Import("colorama", enriched_import.Type.THIRD_PARTY_MODULE)]
        ]

        dep_resolver = DependencyResolver(
            python_moduledir="third_party.python",
            enricher=self.mock_enricher,
            std_lib_modules=sys.stdlib_module_names,
            available_third_party_module_targets={"//third_party/python:colorama"},
            known_dependencies={},
            namespace_to_target={"google.protobuf": Target("//third_party/python3:protobuf")},
            nodes_collator=self.mock_nodes_collector,
        )

        deps = dep_resolver.resolve_deps_for_srcs(Target("//path/to:target"), srcs={"x.py"})
        mock_file_open.assert_called_once_with("path/to/x.py", "r")
        self.mock_nodes_collector.collate.assert_called_once_with(code="import colorama", path="path/to/x.py")
        self.mock_enricher.convert.assert_called_once_with(mock_import_node, pyfile_path="path/to/x.py")
        self.assertEqual({Target("//third_party/python:colorama")}, deps)

        return

    @mock.patch("service.dependency.resolver.get_whatinputs")
    @mock.patch("builtins.open", new_callable=mock.mock_open(read_data="import custom.module"))
    def test_resolve_deps_for_srcs_with_whatinputs_result(
        self,
        mock_file_open: mock.MagicMock,
        mock_get_whatinputs: mock.MagicMock,
    ):
        self.mock_nodes_collector.collate.return_value = [
            mock_import_node := ast.Import(names=[ast.Name(name="custom.module")])
        ]
        mock_file_open.return_value.__enter__.return_value.read.return_value = "import custom.module"
        self.mock_enricher.convert.return_value = [
            [enriched_import.Import("custom.module", enriched_import.Type.MODULE)]
        ]
        mock_get_whatinputs.return_value = WhatInputsResult({"//custom:target"}, set())

        dep_resolver = DependencyResolver(
            python_moduledir="third_party.python",
            enricher=self.mock_enricher,
            std_lib_modules=sys.stdlib_module_names,
            available_third_party_module_targets={"//third_party/python:colorama"},
            known_dependencies={},
            namespace_to_target={"google.protobuf": Target("//third_party/python3:protobuf")},
            nodes_collator=self.mock_nodes_collector,
        )

        deps = dep_resolver.resolve_deps_for_srcs(Target("//path/to:target"), srcs={"y.py"})
        mock_file_open.assert_called_once_with("path/to/y.py", "r")
        self.mock_nodes_collector.collate.assert_called_once_with(code="import custom.module", path="path/to/y.py")
        self.mock_enricher.convert.assert_called_once_with(mock_import_node, pyfile_path="path/to/y.py")
        mock_get_whatinputs.assert_called_once()
        self.assertEqual({Target("//custom:target")}, deps)

        return

    @mock.patch("service.dependency.resolver.get_whatinputs")
    @mock.patch("builtins.open", new_callable=mock.mock_open(read_data="import custom.module"))
    def test_removes_self_dependency(
        self,
        mock_file_open: mock.MagicMock,
        mock_get_whatinputs: mock.MagicMock,
    ):
        self.mock_nodes_collector.collate.return_value = [
            mock_import_node := ast.Import(names=[ast.Name(name="custom.module")])
        ]
        mock_file_open.return_value.__enter__.return_value.read.return_value = "import custom.module, path.to.target"
        self.mock_enricher.convert.return_value = [[enriched_import.Import("custom.module", enriched_import.Type.STUB)]]
        mock_get_whatinputs.return_value = WhatInputsResult({"//path/to:target", "//custom:target"}, set())

        dep_resolver = DependencyResolver(
            python_moduledir="third_party.python",
            enricher=self.mock_enricher,
            std_lib_modules=sys.stdlib_module_names,
            available_third_party_module_targets={"//third_party/python:colorama"},
            known_dependencies={},
            namespace_to_target={"google.protobuf": Target("//third_party/python3:protobuf")},
            nodes_collator=self.mock_nodes_collector,
        )

        deps = dep_resolver.resolve_deps_for_srcs(Target("//path/to:target"), srcs={"z.pyi"})
        mock_file_open.assert_called_once_with("path/to/z.pyi", "r")
        self.mock_nodes_collector.collate.assert_called_once_with(
            code="import custom.module, path.to.target",
            path="path/to/z.pyi",
        )
        self.mock_enricher.convert.assert_called_once_with(mock_import_node, pyfile_path="path/to/z.pyi")
        mock_get_whatinputs.assert_called_once()
        self.assertEqual({Target("//custom:target")}, deps)

        return

    @mock.patch("builtins.open", new_callable=mock.mock_open(read_data="import custom.module"))
    def test_injects_known_dependencies(self, mock_file_open: mock.MagicMock):
        self.mock_nodes_collector.collate.return_value = [
            mock_import_node := ast.Import(names=[ast.Name(name="colorama")])
        ]
        mock_file_open.return_value.__enter__.return_value.read.return_value = "import colorama"
        self.mock_enricher.convert.return_value = [
            [enriched_import.Import("colorama", enriched_import.Type.THIRD_PARTY_MODULE)]
        ]

        dep_resolver = DependencyResolver(
            python_moduledir="third_party.python",
            enricher=self.mock_enricher,
            std_lib_modules=sys.stdlib_module_names,
            available_third_party_module_targets={"//third_party/python:colorama"},
            known_dependencies={"path.to.x": [Target("//injected/pkg:target")]},
            namespace_to_target={"google.protobuf": Target("//third_party/python3:protobuf")},
            nodes_collator=self.mock_nodes_collector,
        )

        deps = dep_resolver.resolve_deps_for_srcs(Target("//path/to:target"), srcs={"x.py"})
        mock_file_open.assert_called_once_with("path/to/x.py", "r")
        self.mock_nodes_collector.collate.assert_called_once_with(code="import colorama", path="path/to/x.py")
        self.mock_enricher.convert.assert_called_once_with(mock_import_node, pyfile_path="path/to/x.py")
        self.assertEqual(
            {Target("//third_party/python:colorama"), Target("//injected/pkg:target")},
            deps,
        )
        return

    @mock.patch("builtins.open", new_callable=mock.mock_open(read_data="import custom.module"))
    def test_injects_namespaced_pkg_targets_when_moduledir_included(self, mock_file_open: mock.MagicMock):
        self.mock_nodes_collator.collate.return_value = [
            mock_import_node := ast.ImportFrom(
                module="third_party.python3.google",
                names=[ast.Name(name="protobuf")],
            )
        ]
        mock_file_open.return_value.__enter__.return_value.read.return_value = (
            "from third_party.python3.google import protobuf"
        )
        self.mock_enricher.convert.return_value = [
            [enriched_import.Import("google.protobuf", enriched_import.Type.UNKNOWN)]
        ]

        dep_resolver = DependencyResolver(
            python_moduledir="third_party.python3",
            enricher=self.mock_enricher,
            std_lib_modules=sys.stdlib_module_names,
            available_third_party_module_targets={"//third_party/python3:protobuf"},
            known_dependencies={},
            namespace_to_target={"google.protobuf": Target("//third_party/python3:protobuf")},
            nodes_collator=self.mock_nodes_collator,
        )

        deps = dep_resolver.resolve_deps_for_srcs(Target("//path/to:target"), srcs={"x.py"})
        mock_file_open.assert_called_once_with("path/to/x.py", "r")
        self.mock_nodes_collator.collate.assert_called_once_with(
            code="from third_party.python3.google import protobuf",
            path="path/to/x.py",
        )
        self.mock_enricher.convert.assert_called_once_with(mock_import_node, pyfile_path="path/to/x.py")
        self.assertEqual(
            {Target("//third_party/python3:protobuf")},
            deps,
        )
        return

    @mock.patch("builtins.open", new_callable=mock.mock_open(read_data="import custom.module"))
    def test_injects_namespaced_pkg_targets(self, mock_file_open: mock.MagicMock):
        self.mock_nodes_collector.collate.return_value = [
            mock_import_node := ast.Import(names=[ast.Name(name="colorama")])
        ]
        mock_file_open.return_value.__enter__.return_value.read.return_value = "import google.protobuf.field_mask_pb2"
        self.mock_enricher.convert.return_value = [
            [enriched_import.Import("google.protobuf", enriched_import.Type.UNKNOWN)]
        ]

        dep_resolver = DependencyResolver(
            python_moduledir="third_party.python3",
            enricher=self.mock_enricher,
            std_lib_modules=sys.stdlib_module_names,
            available_third_party_module_targets={"//third_party/python3:protobuf"},
            known_dependencies={},
            namespace_to_target={"google.protobuf": Target("//third_party/python3:protobuf")},
            nodes_collator=self.mock_nodes_collector,
        )

        deps = dep_resolver.resolve_deps_for_srcs(Target("//path/to:target"), srcs={"x.py"})
        mock_file_open.assert_called_once_with("path/to/x.py", "r")
        self.mock_nodes_collector.collate.assert_called_once_with(
            code="import google.protobuf.field_mask_pb2",
            path="path/to/x.py",
        )
        self.mock_enricher.convert.assert_called_once_with(mock_import_node, pyfile_path="path/to/x.py")
        self.assertEqual(
            {Target("//third_party/python3:protobuf")},
            deps,
        )
        return

    def test_returns_empty_with_no_srcs(self):
        dep_resolver = DependencyResolver(
            python_moduledir="third_party.python",
            enricher=self.mock_enricher,
            std_lib_modules=sys.stdlib_module_names,
            available_third_party_module_targets={"//third_party/python:colorama"},
            known_dependencies={},
            namespace_to_target={},
            nodes_collator=self.mock_nodes_collector,
        )
        self.assertEqual(set(), dep_resolver.resolve_deps_for_srcs(Target("//does/not:matter"), set()))
        return

    def test_ignores_srcs_of_unsupported_filetypes(self):
        dep_resolver = DependencyResolver(
            python_moduledir="third_party.python",
            enricher=self.mock_enricher,
            std_lib_modules=sys.stdlib_module_names,
            available_third_party_module_targets={"//third_party/python:colorama"},
            known_dependencies={},
            namespace_to_target={},
            nodes_collator=self.mock_nodes_collector,
        )

        deps = dep_resolver.resolve_deps_for_srcs(Target("//path/to:target"), srcs={"x.txt", "y.build_def"})
        self.assertEqual(set(), deps)
        return


class TestConvertOSPathToPyImportPath(TestCase):
    def test_dirname(self):
        test_pkg_path = os.path.join("test", "pkg")
        converted = convert_os_path_to_import_path(test_pkg_path)
        self.assertEqual("test.pkg", converted)
        return

    def test_filename(self):
        test_module_path = os.path.join("test", "pkg", "module.py")
        converted = convert_os_path_to_import_path(test_module_path)
        self.assertEqual("test.pkg.module", converted)
        return

    def test_with_project_root(self):
        test_module_path = os.path.abspath(os.path.join("root", "project_root", "test", "pkg", "module.py"))
        converted = convert_os_path_to_import_path(
            test_module_path, os.path.abspath(os.path.join("root", "project_root"))
        )
        self.assertEqual("test.pkg.module", converted)
        return
