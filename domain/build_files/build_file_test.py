import ast
import unittest

from domain.build_files.build_file import BUILDFile
from domain.targets.target import PythonLibrary


class TestBuildFile(unittest.TestCase):
    def test_add_target(self):
        build_file = BUILDFile(ast.Module(body=[], type_ignores=[]))
        build_file.add_target(
            PythonLibrary(name="x", srcs={"x.py", "y.py"}, deps={"//path/to:target", ":x"}, visibility={"PUBLIC"}),
        )
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
                                        value=ast.List(elts=[ast.Constant(value="x.py"), ast.Constant(value="y.py")]),
                                    ),
                                    ast.keyword(
                                        arg="deps",
                                        value=ast.List(
                                            elts=[ast.Constant(value="//path/to:target"), ast.Constant(value=":x")],
                                        ),
                                    ),
                                    ast.keyword(arg="visibility", value=ast.List(elts=[ast.Constant(value="PUBLIC")])),
                                ]
                            )
                        ),
                    ],
                    type_ignores=[],
                )
            ),
            ast.unparse(build_file._ast_repr),
        )

        return

    def test_dump_ast(self):
        build_file = BUILDFile(ast.Module(body=[], type_ignores=[]))
        build_file.add_target(
            PythonLibrary(name="x", srcs={"x.py", "y.py"}, deps={"dep_2.py", "dep_1.py"}, visibility={"PUBLIC"}))
        self.assertEqual(
            "python_library(name='x', srcs=['x.py', 'y.py'], deps=['dep_1.py', 'dep_2.py'], visibility=['PUBLIC'])",
            build_file.dump_ast(),
        )
        return
