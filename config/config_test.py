from collections import namedtuple
from unittest import TestCase

import jsonschema

from config.config import _validate


class TestConfigValidation(TestCase):
    def test_raises_validation_err_when_invalid_schema(self):
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
        ]

        for testcase in subtests:
            with self.subTest(testcase.name):
                self.assertRaises(
                    jsonschema.exceptions.ValidationError,
                    _validate,
                    {"knownDependencies": testcase.known_dependencies},
                )
        return
