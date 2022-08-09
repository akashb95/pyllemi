import ast
import unittest

from domain.plz.rule.utils import get_ast_nodes_to_manage


class TestBuildFile(unittest.TestCase):
    def test_get_existing_ast_python_build_rules(self):
        python_library = ast.Call(
            func=ast.Name(id="python_library"),
            args=[],
            keywords=[
                ast.keyword(arg="name", value=ast.Constant(value="x")),
                ast.keyword(
                    arg="srcs",
                    value=ast.List(elts=[ast.Constant(value="x.py"), ast.Constant(value="y.py")]),
                ),
                ast.keyword(
                    arg="deps",
                    value=ast.List(
                        elts=[
                            ast.Constant(value="//path/to:target"),
                            ast.Constant(value=":z"),
                        ],
                    ),
                ),
            ],
        )
        python_test = ast.Call(
            func=ast.Name(id="python_test"),
            args=[],
            keywords=[
                ast.keyword(arg="name", value=ast.Constant(value="x_test")),
                ast.keyword(
                    arg="srcs",
                    value=ast.List(
                        elts=[
                            ast.Constant(value="x_test.py"),
                            ast.Constant(value="y_test.py"),
                        ]
                    ),
                ),
                ast.keyword(
                    arg="deps",
                    value=ast.List(
                        elts=[
                            ast.Constant(value="//path/to:target"),
                            ast.Constant(value=":x"),
                        ],
                    ),
                ),
            ],
        )

        custom_rule_target = ast.Call(
            func=ast.Name(id="custom_rule_to_manage"),
            args=[],
            keywords=[
                ast.keyword(arg="name", value=ast.Constant(value="x_test")),
                ast.keyword(
                    arg="srcs",
                    value=ast.List(
                        elts=[
                            ast.Constant(value="x_test.py"),
                            ast.Constant(value="y_test.py"),
                        ]
                    ),
                ),
                ast.keyword(
                    arg="deps",
                    value=ast.List(
                        elts=[
                            ast.Constant(value="//path/to:target"),
                            ast.Constant(value=":x"),
                        ],
                    ),
                ),
            ],
        )

        root = ast.Module(
            body=[
                ast.Expr(ast.Call(func=ast.Name(id="should_not_matter"))),
                ast.Expr(python_library),
                ast.Expr(python_test),
                ast.Expr(ast.Call(func=ast.Name(id="should_not_matter_either"))),
                ast.Expr(custom_rule_target),
            ],
            type_ignores=[],
        )

        self.assertEqual(
            {python_library, python_test, custom_rule_target},
            get_ast_nodes_to_manage(root, custom_rules_to_manage={"custom_rule_to_manage"}),
        )
        return
