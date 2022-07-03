from unittest import TestCase

from config.known_dependencies import get_from_config
from domain.plz.target.target import Target, InvalidPlzTargetError


class TestKnown(TestCase):
    def test_from_config(self):
        self.assertEqual(
            {
                "pkg.subpkg.module": [Target("//pkg/subpkg:module")],
                "pkg.another_subpkg.module": [Target("//pkg/another_subpkg")],
            },
            get_from_config(
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
        self.assertEqual({}, get_from_config({"someOtherKey": ["x", "y"]}))
        return

    def test_propagates_err_when_invalid_plz_target(self):
        self.assertRaises(
            InvalidPlzTargetError,
            get_from_config,
            {"knownDependencies": [{"module": "x", "plzTarget": "//under handed"}]},
        )
        return
