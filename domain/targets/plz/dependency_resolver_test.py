import ast
import sys
from unittest import mock, TestCase

from adapters.plz_query import WhatInputsResult
from domain.imports.enriched_import import EnrichedImport, ImportType
from domain.targets.plz.dependency_resolver import DependencyResolver
from domain.targets.plz_target import PlzTarget


class MyTestCase(TestCase):
    def setUp(self) -> None:
        self.mock_nodes_collator = mock.MagicMock()
        self.mock_enricher = mock.MagicMock()
        return

    @mock.patch("builtins.open", new_callable=mock.mock_open(read_data="import colorama"))
    def test_resolve_deps_for_srcs_with_third_party_module(self, mock_file_open: mock.MagicMock):
        self.mock_nodes_collator.collate.return_value = [
            mock_import_node := ast.Import(names=[ast.Name(name="colorama")])
        ]
        mock_file_open.return_value.__enter__.return_value.read.return_value = "import colorama"
        self.mock_enricher.convert.return_value = [[EnrichedImport("colorama", ImportType.THIRD_PARTY_MODULE)]]

        dep_resolver = DependencyResolver(
            python_moduledir="third_party.python",
            enricher=self.mock_enricher,
            std_lib_modules=sys.stdlib_module_names,
            available_third_party_module_targets={"//third_party/python:colorama"},
            nodes_collator=self.mock_nodes_collator,
        )

        deps = dep_resolver.resolve_deps_for_srcs(PlzTarget("//path/to:target"), srcs={"x.py"})
        mock_file_open.assert_called_once_with("path/to/x.py", "r")
        self.mock_nodes_collator.collate.assert_called_once_with(code="import colorama", path="path/to/x.py")
        self.mock_enricher.convert.assert_called_once_with(mock_import_node)
        self.assertEqual({"//third_party/python:colorama"}, deps)

        return

    @mock.patch("domain.targets.plz.dependency_resolver.get_whatinputs")
    @mock.patch("builtins.open", new_callable=mock.mock_open(read_data="import custom.module"))
    def test_resolve_deps_for_srcs_with_whatinputs_result(
        self,
        mock_file_open: mock.MagicMock,
        mock_get_whatinputs: mock.MagicMock,
    ):
        self.mock_nodes_collator.collate.return_value = [
            mock_import_node := ast.Import(names=[ast.Name(name="custom.module")])
        ]
        mock_file_open.return_value.__enter__.return_value.read.return_value = "import custom.module"
        self.mock_enricher.convert.return_value = [[EnrichedImport("custom.module", ImportType.MODULE)]]
        mock_get_whatinputs.return_value = WhatInputsResult({"//custom:target"}, set())

        dep_resolver = DependencyResolver(
            python_moduledir="third_party.python",
            enricher=self.mock_enricher,
            std_lib_modules=sys.stdlib_module_names,
            available_third_party_module_targets={"//third_party/python:colorama"},
            nodes_collator=self.mock_nodes_collator,
        )

        deps = dep_resolver.resolve_deps_for_srcs(PlzTarget("//path/to:target"), srcs={"y.py"})
        mock_file_open.assert_called_once_with("path/to/y.py", "r")
        self.mock_nodes_collator.collate.assert_called_once_with(code="import custom.module", path="path/to/y.py")
        self.mock_enricher.convert.assert_called_once_with(mock_import_node)
        mock_get_whatinputs.assert_called_once()
        self.assertEqual({"//custom:target"}, deps)

        return

    @mock.patch("domain.targets.plz.dependency_resolver.get_whatinputs")
    @mock.patch("builtins.open", new_callable=mock.mock_open(read_data="import custom.module"))
    def test_removes_self_dependency(
        self,
        mock_file_open: mock.MagicMock,
        mock_get_whatinputs: mock.MagicMock,
    ):
        self.mock_nodes_collator.collate.return_value = [
            mock_import_node := ast.Import(names=[ast.Name(name="custom.module")])
        ]
        mock_file_open.return_value.__enter__.return_value.read.return_value = "import custom.module, path.to.target"
        self.mock_enricher.convert.return_value = [[EnrichedImport("custom.module", ImportType.STUB)]]
        mock_get_whatinputs.return_value = WhatInputsResult({"//path/to:target", "//custom:target"}, set())

        dep_resolver = DependencyResolver(
            python_moduledir="third_party.python",
            enricher=self.mock_enricher,
            std_lib_modules=sys.stdlib_module_names,
            available_third_party_module_targets={"//third_party/python:colorama"},
            nodes_collator=self.mock_nodes_collator,
        )

        deps = dep_resolver.resolve_deps_for_srcs(PlzTarget("//path/to:target"), srcs={"z.pyi"})
        mock_file_open.assert_called_once_with("path/to/z.pyi", "r")
        self.mock_nodes_collator.collate.assert_called_once_with(
            code="import custom.module, path.to.target",
            path="path/to/z.pyi",
        )
        self.mock_enricher.convert.assert_called_once_with(mock_import_node)
        mock_get_whatinputs.assert_called_once()
        self.assertEqual({"//custom:target"}, deps)

        return

    def test_returns_empty_with_no_srcs(self):
        dep_resolver = DependencyResolver(
            python_moduledir="third_party.python",
            enricher=self.mock_enricher,
            std_lib_modules=sys.stdlib_module_names,
            available_third_party_module_targets={"//third_party/python:colorama"},
            nodes_collator=self.mock_nodes_collator,
        )
        self.assertEqual(set(), dep_resolver.resolve_deps_for_srcs(PlzTarget("//does/not:matter"), set()))
        return
