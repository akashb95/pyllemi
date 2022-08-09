from collections import namedtuple
from unittest import TestCase

import jsonschema

from config.config import _validate


class TestConfigValidation(TestCase):
    def test_raises_validation_err_when_invalid_schema_for_known_dependencies(self):
        SubTest = namedtuple("SubTest", ["name", "known_dependencies"])
        subtests = [
            SubTest(
                name="empty module",
                known_dependencies=[
                    {"module": "", "plzTarget": "//path/to:target"},
                ],
            ),
            SubTest(
                name="invalid plz target path pattern (relative)",
                known_dependencies=[
                    {"module": "x.y.z", "plzTarget": ":x"},
                ],
            ),
            SubTest(
                name="invalid plz target path pattern (relative)",
                known_dependencies=[
                    {"module": "x.y.z", "plzTarget": ":x"},
                ],
            ),
            SubTest(
                name="missing module attr",
                known_dependencies=[{"plzTarget": "//x"}],
            ),
            SubTest(
                name="missing plzTarget attr",
                known_dependencies=[{"module": "x"}],
            ),
            SubTest(
                name="additional property",
                known_dependencies=[{"module": "x", "plzTarget": "//x", "doesNotBelongHere": "blah"}],
            ),
        ]

        for testcase in subtests:
            with self.subTest(testcase.name):
                self.assertRaises(
                    jsonschema.exceptions.ValidationError,
                    _validate,
                    {"knownDependencies": testcase.known_dependencies},
                )
        return

    def test_raises_err_when_invalid_schema_for_known_namespaces(self):
        SubTest = namedtuple("SubTest", ["name", "known_namespaces"])
        subtests = [
            SubTest(
                name="empty namespace",
                known_namespaces=[
                    {"namespace": "", "plzTarget": "//path/to:target"},
                ],
            ),
            SubTest(
                name="invalid plz target path pattern (relative)",
                known_namespaces=[
                    {"namespace": "x.y.z", "plzTarget": ":x"},
                ],
            ),
            SubTest(
                name="missing namespace attr",
                known_namespaces=[{"plzTarget": "//x"}],
            ),
            SubTest(
                name="missing plzTarget attr",
                known_namespaces=[{"namespace": "x"}],
            ),
            SubTest(
                name="additional property",
                known_namespaces=[{"namespace": "x", "plzTarget": "//x", "doesNotBelongHere": "blah"}],
            ),
        ]

        for testcase in subtests:
            with self.subTest(testcase.name):
                self.assertRaises(
                    jsonschema.exceptions.ValidationError,
                    _validate,
                    {"knownNamespaces": testcase.known_namespaces},
                )
        return

    def test_raises_validation_err_when_invalid_schema_for_custom_rules_to_manage(self):
        SubTest = namedtuple("SubTest", ["name", "custom_rules_to_manage"])
        subtests = [
            SubTest(
                name="contains empty string",
                custom_rules_to_manage=[""],
            ),
        ]

        for testcase in subtests:
            with self.subTest(testcase.name):
                self.assertRaises(
                    jsonschema.exceptions.ValidationError,
                    _validate,
                    {"knownDependencies": testcase.custom_rules_to_manage},
                )
        return
