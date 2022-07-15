from unittest import TestCase

from config.known_namespace_packages import get_from_config, DuplicateKnownNamespacePackagesError
from config.schema import KNOWN_NAMESPACES_KEY
from domain.plz.target.target import Target, InvalidPlzTargetError


class TestKnownNamespacePkgs(TestCase):
    def test_with_no_known_namespace_pkgs(self):
        self.assertEqual({}, get_from_config({"someOtherKey": [{"x": "y"}, {"a": "b"}]}))
        return

    def test_from_config(self):
        self.assertEqual(
            {
                "google.protobuf": Target("//third_party/python3:protobuf"),
                "potato": Target("//some:potato"),
            },
            get_from_config(
                {
                    KNOWN_NAMESPACES_KEY: [
                        {
                            "namespace": "google.protobuf",
                            "plzTarget": "//third_party/python3:protobuf",
                        },
                        {
                            "namespace": "potato",
                            "plzTarget": "//some:potato",
                        },
                    ],
                },
            ),
        )
        return

    def test_from_config_raises_err_when_duplicate_entries_found(self):
        self.assertRaisesRegex(
            DuplicateKnownNamespacePackagesError,
            "found multiple entries in config for the following known namespace pkgs: .*google.protobuf.*",
            get_from_config,
            {
                KNOWN_NAMESPACES_KEY: [
                    {
                        "namespace": "google.protobuf",
                        "plzTarget": "//third_party/python3:protobuf",
                    },
                    {
                        "namespace": "google.protobuf",
                        "plzTarget": "//duplicate:protobuf",
                    },
                ],
            },
        )
        return

    def test_propagates_err_when_invalid_plz_target(self):
        self.assertRaises(
            InvalidPlzTargetError,
            get_from_config,
            {KNOWN_NAMESPACES_KEY: [{"namespace": "x", "plzTarget": "//under handed"}]},
        )
        return
