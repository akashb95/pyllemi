import ast
from unittest import TestCase, mock

from domain.targets.converters import from_ast_node_to_python_target
from domain.targets.plz_target import PlzTarget
from domain.targets.python_target import PythonLibrary, PythonTest, PythonBinary


class ConvertersTest(TestCase):
    def test_converts_python_library(self):
        input_ast_node = ast.parse("python_library(name='lib', srcs=['input.py'], deps=[':dep'])")
        self.assertEqual(
            PythonLibrary(name="lib", srcs={"input.py"}, deps={":dep"}),
            from_ast_node_to_python_target(input_ast_node.body[0].value, "path/to/lib"),
        )
        return

    def test_converts_python_test(self):
        input_ast_node = ast.parse("python_test(name='test', srcs=['lib_test.py'], deps=[':lib'])")
        self.assertEqual(
            PythonTest(name="test", srcs={"lib_test.py"}, deps={":lib"}),
            from_ast_node_to_python_target(input_ast_node.body[0].value, "//path/to/test"),
        )
        return

    def test_converts_python_binary(self):
        input_ast_node = ast.parse("python_binary(name='bin', main='main.py', deps=[':dep'])")
        self.assertEqual(
            PythonBinary(name="bin", main="main.py", deps={":dep"}),
            from_ast_node_to_python_target(input_ast_node.body[0].value, "//path/to/bin"),
        )
        return

    @mock.patch("domain.targets.converters.get_print")
    def test_fetches_srcs_via_plz_query_if_srcs_is_not_list(self, mock_plz_query_print: mock.MagicMock):
        with self.subTest("python_library"):
            input_ast_node = ast.parse("python_library(name='target', srcs=glob(['*.py'], exclude=['*_test.py']))")
            mock_plz_query_print.return_value = ["__init__.py", "module.py"]
            self.assertEqual(
                PythonLibrary(name="target", srcs={"__init__.py", "module.py"}, deps=set()),
                from_ast_node_to_python_target(input_ast_node.body[0].value, "path/to"),
            )
            mock_plz_query_print.assert_called_once_with("//path/to:target", "srcs")

        mock_plz_query_print.reset_mock()

        with self.subTest("python_test"):
            input_ast_node = ast.parse("python_test(name='test', srcs=glob(['*_test.py']))")
            mock_plz_query_print.return_value = ["module_test.py"]
            self.assertEqual(
                PythonTest(name="test", srcs={"module_test.py"}, deps=set()),
                from_ast_node_to_python_target(input_ast_node.body[0].value, "path/to"),
            )
            mock_plz_query_print.assert_called_once_with("//path/to:_test#lib", "srcs")
        return

    def test_errors_if_not_ast_call(self):
        self.assertRaisesRegex(
            TypeError,
            "AST node is of type Module; expected Call",
            from_ast_node_to_python_target,
            ast.Module(),
            "//does/not:matter",
        )
        return

    def test_errors_if_func_id_not_python_build_rule(self):
        self.assertRaisesRegex(
            ValueError,
            "BUILD rule call function is called 'not_valid', which is not a supported Python rule",
            from_ast_node_to_python_target,
            ast.parse("not_valid(name='target', srcs=glob(['*.py'], exclude=['*_test.py']))").body[0].value,
            "//does/not:matter",
        )
        return
