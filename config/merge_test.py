from collections import namedtuple
from unittest import TestCase

from config.merge import _merge_bool_property, _merge_dict_property
from config.schema import USE_GLOBS_AS_SRCS_KEY, KNOWN_NAMESPACES_KEY, KNOWN_DEPENDENCIES_KEY


class TestMerge(TestCase):
    def test__merge_bool_property(self):
        with self.subTest("overrides parent values"):
            self.assertFalse(
                _merge_bool_property(
                    USE_GLOBS_AS_SRCS_KEY,
                    [
                        {USE_GLOBS_AS_SRCS_KEY: False, KNOWN_NAMESPACES_KEY: {}, KNOWN_DEPENDENCIES_KEY: {}},
                        {USE_GLOBS_AS_SRCS_KEY: True, KNOWN_NAMESPACES_KEY: {"x.y": "//x:y"}},
                        {USE_GLOBS_AS_SRCS_KEY: False, KNOWN_DEPENDENCIES_KEY: {"x.y": "//a/b:c"}},
                        {USE_GLOBS_AS_SRCS_KEY: False},
                    ],
                    default=False,
                ),
            )

        with self.subTest("inherits true value"):
            self.assertTrue(
                _merge_bool_property(
                    USE_GLOBS_AS_SRCS_KEY,
                    [
                        {KNOWN_NAMESPACES_KEY: {}, KNOWN_DEPENDENCIES_KEY: {}},
                        {USE_GLOBS_AS_SRCS_KEY: True, KNOWN_NAMESPACES_KEY: {"x.y": "//x:y"}},
                        {USE_GLOBS_AS_SRCS_KEY: False, KNOWN_DEPENDENCIES_KEY: {"x.y": "//a/b:c"}},
                        {USE_GLOBS_AS_SRCS_KEY: True},
                    ],
                    default=False,
                ),
            )

        with self.subTest("inherits false value"):
            self.assertFalse(
                _merge_bool_property(
                    USE_GLOBS_AS_SRCS_KEY,
                    [
                        {KNOWN_NAMESPACES_KEY: {}, KNOWN_DEPENDENCIES_KEY: {}},
                        {USE_GLOBS_AS_SRCS_KEY: False, KNOWN_NAMESPACES_KEY: {"x.y": "//x:y"}},
                        {USE_GLOBS_AS_SRCS_KEY: True, KNOWN_DEPENDENCIES_KEY: {"x.y": "//a/b:c"}},
                        {USE_GLOBS_AS_SRCS_KEY: True},
                    ],
                    default=False,
                ),
            )

        return

    def test__merge_dict_property_with(self):
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
