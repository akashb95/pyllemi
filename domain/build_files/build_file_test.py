import ast
import unittest

from config.config import Config
from domain.build_files.build_file import BUILDFile
from domain.plz.rule.python import Python, Library


class TestBuildFile(unittest.TestCase):
    def test_parses_custom_rule_targets_into_ast(self):
        build_file = BUILDFile(
            ast.Module(body=[], type_ignores=[]), config=Config(custom_rules_to_manage={"custom_rule"})
        )
        build_file.add_new_target(
            Python(name="x", rule_name="custom_rule", srcs={"x.py", "y.py"}, deps={"//path/to:target", ":x"}),
        )
        build_file._add_new_targets_to_ast()
        # noinspection PyTypeChecker
        self.assertEqual(
            ast.unparse(
                ast.Module(
                    body=[
                        ast.Expr(
                            ast.Call(
                                func=ast.Name(id="custom_rule"),
                                args=[],
                                keywords=[
                                    ast.keyword(arg="name", value=ast.Constant(value="x")),
                                    ast.keyword(
                                        arg="srcs",
                                        value=ast.List(
                                            elts=[
                                                ast.Constant(value="x.py"),
                                                ast.Constant(value="y.py"),
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
                        ),
                    ],
                    type_ignores=[],
                )
            ),
            ast.unparse(build_file._ast_repr),
        )
        return

    def test_parses_new_targets_into_ast(self):
        build_file = BUILDFile(ast.Module(body=[], type_ignores=[]), config=Config())
        build_file.add_new_target(
            Library(name="x", srcs={"x.py", "y.py"}, deps={"//path/to:target", ":x"}),
        )
        build_file._add_new_targets_to_ast()
        # noinspection PyTypeChecker
        self.assertEqual(
            ast.unparse(
                ast.Module(
                    body=[
                        ast.Expr(
                            ast.Call(
                                func=ast.Name(id="python_library"),
                                args=[],
                                keywords=[
                                    ast.keyword(arg="name", value=ast.Constant(value="x")),
                                    ast.keyword(
                                        arg="srcs",
                                        value=ast.List(
                                            elts=[
                                                ast.Constant(value="x.py"),
                                                ast.Constant(value="y.py"),
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
                        ),
                    ],
                    type_ignores=[],
                )
            ),
            ast.unparse(build_file._ast_repr),
        )

        return

    def test_register_modified_build_rule_to_python_target(self):
        build_rule = ast.Call(
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
                            ast.Constant(value=":x"),
                        ],
                    ),
                ),
            ],
        )
        build_file = BUILDFile(ast.Module(body=[ast.Expr(build_rule)], type_ignores=[]), config=Config())
        build_rule_as_domain_target = Library(
            name="x",
            srcs={"x.py", "y.py"},
            deps={"//path/to:target", ":x"},
        )
        build_file.register_modified_build_rule_to_python_target(build_rule, build_rule_as_domain_target)

        # Modify target (mock dependency alteration)
        build_rule_as_domain_target.kwargs["deps"] = {":dep_2", ":dep_1"}
        build_file._reflect_changes_to_python_targets_in_ast()

        expected_modified_build_rule = ast.Call(
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
                            ast.Constant(value=":dep_1"),
                            ast.Constant(value=":dep_2"),
                        ],
                    ),
                ),
            ],
        )
        self.assertEqual(
            ast.unparse(ast.Module(body=[ast.Expr(expected_modified_build_rule)], type_ignores=[])),
            ast.unparse(build_file._ast_repr),
        )
        return

    def test_dump_ast_when_build_file_is_empty(self):
        build_file = BUILDFile(ast.Module(body=[], type_ignores=[]), config=Config())
        build_file.add_new_target(Library(name="x", srcs={"x.py", "y.py"}, deps={"dep_2.py", "dep_1.py"}))
        self.assertEqual(
            "python_library(name='x', srcs=['x.py', 'y.py'], deps=['dep_1.py', 'dep_2.py'])",
            build_file.dump_ast(),
        )
        return

    def test_dump_ast_when_build_file_has_preexisting_targets(self):
        build_rule = ast.Call(
            func=ast.Name(id="python_library"),
            args=[],
            keywords=[
                ast.keyword(arg="name", value=ast.Constant(value="x")),
                ast.keyword(
                    arg="srcs",
                    value=ast.List(elts=[ast.Constant(value="x.py"), ast.Constant(value="y.py")]),
                ),
                # deliberately missing the deps keyword.
            ],
        )
        build_file = BUILDFile(ast.Module(body=[build_rule], type_ignores=[]), config=Config())
        build_file.register_modified_build_rule_to_python_target(
            build_rule,
            Library(name="x", srcs={"x.py", "y.py"}, deps={"dep_2.py", "dep_1.py"}),
        )

        self.assertEqual(
            "python_library(name='x', srcs=['x.py', 'y.py'], deps=['dep_1.py', 'dep_2.py'])",
            build_file.dump_ast(),
        )

        return
