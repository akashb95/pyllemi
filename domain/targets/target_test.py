import collections
import unittest

from domain.targets.python_target import PythonTargetTypes, Target


class TestTarget(unittest.TestCase):
    def test_target_type(self):
        SubTest = collections.namedtuple("SubTest", ("rule_name", "expected_target_type"))
        subtests: list[SubTest] = [
            SubTest("python_library", PythonTargetTypes.PYTHON_LIBRARY),
            SubTest("python_test", PythonTargetTypes.PYTHON_TEST),
            SubTest("python_binary", PythonTargetTypes.PYTHON_BINARY),
            SubTest("does_not_exist", PythonTargetTypes.UNKNOWN),
        ]

        for subtest in subtests:
            with self.subTest(subtest.rule_name):
                target = Target(rule_name=subtest.rule_name)
                self.assertEqual(subtest.expected_target_type, target.type_)
