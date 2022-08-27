from collections import namedtuple
from unittest import TestCase

from config.config import Config
from config.merge import _get_effective_list_property, _merge_bool_property, _merge_dict_property, merge
from config.schema import KNOWN_NAMESPACES_KEY
from domain.plz.target.target import Target


class TestMerge(TestCase):
    def test__merge_bool_property(self):
        with self.subTest("overrides parent values"):
            self.assertFalse(
                _merge_bool_property(
                    [False, True, False, False],
                    default=False,
                ),
            )

        with self.subTest("inherits true value"):
            self.assertTrue(
                _merge_bool_property(
                    [None, True, False, True],
                    default=False,
                ),
            )

        with self.subTest("inherits false value"):
            self.assertFalse(
                _merge_bool_property(
                    [None, False, True, True],
                    default=False,
                ),
            )

        with self.subTest("respects default"):
            self.assertTrue(
                _merge_bool_property(
                    [None, None],
                    default=True,
                ),
            )
        return

    def test__get_effective_list_property(self):
        SubTest = namedtuple("SubTest", ["name", "input", "expected_output"])
        testcases = [
            SubTest(
                name="empty values returns effective list of empty value",
                input=[set(), set(), set()],
                expected_output=set(),
            ),
            SubTest(
                name="highest precedence value overrides lower precedence values",
                input=[{"override"}, {"overridden"}, set()],
                expected_output={"override"},
            ),
            SubTest(
                name="takes highest precedence non-zero value",
                input=[set(), {"defaults", "to", "this"}, set()],
                expected_output={"defaults", "to", "this"},
            ),
        ]

        for testcase in testcases:
            with self.subTest(testcase.name):
                self.assertEqual(testcase.expected_output, _get_effective_list_property(testcase.input))
        return

    def test__merge_dict_property(self):
        SubTest = namedtuple("SubTest", ["name", "key", "input", "expected_output"])
        testcases = [
            SubTest(
                name="overrides parent config",
                key=KNOWN_NAMESPACES_KEY,
                input=[
                    {"x.y.z": "//x/y:z1", "a.b.c": ["//a/b:c"]},
                    {"x.y.z": "//x/y:z2", "a.b.c": ["//blah"]},
                    {"x.y.z": "//x/y:z3"},
                ],
                expected_output={"x.y.z": "//x/y:z1", "a.b.c": ["//a/b:c"]},
            ),
            SubTest(
                name="inherits parent config",
                key=KNOWN_NAMESPACES_KEY,
                input=[
                    {"x.y.z": "//x/y:z"},
                    {"x.y.z": "//x/y:z"},
                    {"x.y.z": "//x/y:z", "a.b.c": ["//a/b:c"]},
                ],
                expected_output={"x.y.z": "//x/y:z", "a.b.c": ["//a/b:c"]},
            ),
        ]

        for testcase in testcases:
            with self.subTest(testcase.name):
                self.assertEqual(
                    testcase.expected_output,
                    _merge_dict_property(testcase.input),
                )
        return

    def test_merge(self):
        configs = [
            Config(
                known_deps={"a.b.c": [Target("//a/b:c")]},
                known_namespaces={},
                no_prune=None,
                use_glob_as_srcs=None,
            ),
            Config(
                known_deps={"d.e.f": [Target("//d/e:f")]},
                known_namespaces={"google.protobuf": Target("//third_party/python3:protobuf")},
                no_prune=True,
                use_glob_as_srcs=False,
            ),
            Config(
                custom_rules_to_manage={"custom_python_rule"},
                known_deps={"a.b.c": [Target("//to/be:overridden"), Target("//to/be:overridden_2")]},
                no_prune=False,
                use_glob_as_srcs=True,
            ),
        ]
        self.assertEqual(
            Config(
                custom_rules_to_manage={"custom_python_rule"},
                known_deps={"a.b.c": [Target("//a/b:c")], "d.e.f": [Target("//d/e:f")]},
                known_namespaces={"google.protobuf": Target("//third_party/python3:protobuf")},
                no_prune=True,
                use_glob_as_srcs=False,
            ),
            merge(configs),
        )
        return
