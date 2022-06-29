from collections import namedtuple
from unittest import TestCase

import jsonschema.exceptions

from domain.imports.known.known import known_dependencies_from_config
from domain.plz.target.target import PlzTarget, InvalidPlzTargetError


class TestKnown(TestCase):
    def test_from_config(self):
        self.assertEqual(
            {
                "pkg.subpkg.module": [PlzTarget("//pkg/subpkg:module")],
                "pkg.another_subpkg.module": [PlzTarget("//pkg/another_subpkg")],
            },
            known_dependencies_from_config(
                {
                    "knownDependencies": [
                        {
                            "module": "pkg.subpkg.module",
                            "plzTarget": "//pkg/subpkg:module",
                        },
                        {
                            "module": "pkg.another_subpkg.module",
                            # Deliberately pass in non-simplified target path to check the in-memory
                            # representation is simplified correctly.
                            "plzTarget": "//pkg/another_subpkg:another_subpkg",
                        },
                    ],
                },
            ),
        )
        return

    def test_with_no_known_deps(self):
        self.assertEqual({}, known_dependencies_from_config({"someOtherKey": ["x", "y"]}))
        return

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
                    known_dependencies_from_config,
                    {"knownDependencies": testcase.known_dependencies},
                )
        return

    def test_propagates_err_when_invalid_plz_target(self):
        self.assertRaises(
            InvalidPlzTargetError,
            known_dependencies_from_config,
            {"knownDependencies": [{"module": "x", "plzTarget": "//under handed"}]},
        )
        return
