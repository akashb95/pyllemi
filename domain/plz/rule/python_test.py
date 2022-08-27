import unittest

from domain.plz.rule.python import Binary, Library, Python, Test
from domain.plz.rule.rule import Types


class TestTarget(unittest.TestCase):
    def test_initialise_python_binary(self):
        binary = Binary(name="bin", main="main.py", deps=set())
        self.assertEqual(Types.PYTHON_BINARY, binary.type_)
        return

    def test_initialise_python_library(self):
        library = Library(name="lib", srcs={"src.py"}, deps=set())
        self.assertEqual(Types.PYTHON_LIBRARY, library.type_)
        return

    def test_initialise_python_test(self):
        test = Test(name="test", srcs={"src_test.py"}, deps=set())
        self.assertEqual(Types.PYTHON_TEST, test.type_)
        return

    def test_initialise_custom_python_rule(self):
        rule = Python(rule_name="custom_python_rule", name="lib", srcs={"src.py"}, deps=set())
        self.assertEqual(Types.UNKNOWN, rule.type_)
        return

    def test_equality(self):
        binary = Binary(name="bin", main="main.py", deps={":target_1", ":target_2"})
        self.assertEqual(
            Binary(name="bin", main="main.py", deps={":target_2", ":target_1"}),
            binary,
        )
        return

    def test_get_item(self):
        binary = Binary(name="bin", main="main.py", deps={":target_1", ":target_2"})
        self.assertEqual(
            {":target_1", ":target_2"},
            binary["deps"],
        )
        return

    def test_set_item_with_modifiable_attribute(self):
        binary = Binary(name="bin", main="main.py", deps={":target_1", ":target_2"})
        binary["deps"] = set()

        self.assertEqual(set(), binary["deps"])
        return
