import ast
from unittest import TestCase, mock

from domain.plz.rule.python import Library, Test, Binary, Python
from service.ast.converters.to_python_rule import convert


class ToPythonRuleTest(TestCase):
    def test_converts_python_library(self):
        input_ast_node = ast.parse("python_library(name='lib', srcs=['input.py'], deps=[':dep'])")
        self.assertEqual(
            Library(name="lib", srcs={"input.py"}, deps={":dep"}),
            convert(input_ast_node.body[0].value, build_pkg_dir="path/to/lib", custom_rules_to_manage=set()),
        )
        return

    def test_converts_python_test(self):
        input_ast_node = ast.parse("python_test(name='test', srcs=['lib_test.py'], deps=[':lib'])")
        self.assertEqual(
            Test(name="test", srcs={"lib_test.py"}, deps={":lib"}),
            convert(input_ast_node.body[0].value, build_pkg_dir="//path/to/test", custom_rules_to_manage=set()),
        )
        return

    def test_converts_python_binary(self):
        input_ast_node = ast.parse("python_binary(name='bin', main='main.py', deps=[':dep'])")
        self.assertEqual(
            Binary(name="bin", main="main.py", deps={":dep"}),
            convert(input_ast_node.body[0].value, build_pkg_dir="//path/to/bin", custom_rules_to_manage=set()),
        )
        return

    @mock.patch("service.ast.converters.to_python_rule.get_print")
    def test_fetches_python_library_srcs_via_plz_query_if_srcs_is_not_list(self, mock_plz_query_print: mock.MagicMock):
        input_ast_node = ast.parse("python_library(name='target', srcs=glob(['*.py'], exclude=['*_test.py']))")
        mock_plz_query_print.side_effect = [
            # Trying to get srcs expected from an underlying python_test-generated rule
            # will raise an error because no such target exists.
            RuntimeError("1"),
            ["__init__.py", "module.py"],
        ]
        self.assertEqual(
            Library(name="target", srcs={"__init__.py", "module.py"}, deps=set()),
            convert(input_ast_node.body[0].value, build_pkg_dir="path/to", custom_rules_to_manage=set()),
        )
        mock_plz_query_print.assert_has_calls(
            [
                mock.call("//path/to:_target#lib", "srcs"),
                mock.call("//path/to:target", "srcs"),
            ]
        )
        return

    @mock.patch("service.ast.converters.to_python_rule.get_print")
    def test_fetches_python_test_srcs_via_plz_query_if_srcs_is_not_list(self, mock_plz_query_print: mock.MagicMock):
        input_ast_node = ast.parse("python_test(name='test', srcs=glob(['*_test.py']))")
        mock_plz_query_print.return_value = ["module_test.py"]
        self.assertEqual(
            Python(rule_name="python_test", name="test", srcs={"module_test.py"}, deps=set()),
            convert(input_ast_node.body[0].value, build_pkg_dir="path/to", custom_rules_to_manage=set()),
        )
        mock_plz_query_print.assert_called_once_with("//path/to:_test#lib", "srcs")
        return

    def test_errors_if_not_ast_call(self):
        self.assertRaisesRegex(
            TypeError,
            "AST node is of type Module; expected Call",
            convert,
            ast.Module(),
            build_pkg_dir="//does/not:matter",
            custom_rules_to_manage=set(),
        )
        return

    def test_errors_if_func_id_not_python_build_rule(self):
        self.assertRaisesRegex(
            ValueError,
            "BUILD rule call function is called 'not_valid', which is not a supported Python rule",
            convert,
            ast.parse("not_valid(name='target', srcs=glob(['*.py'], exclude=['*_test.py']))").body[0].value,
            build_pkg_dir="//does/not:matter",
            custom_rules_to_manage=set(),
        )
        return
