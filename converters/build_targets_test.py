import os
from unittest import TestCase
from converters.build_targets import third_party_import_to_plz_target


class TestThirdPartyImportToPlzTarget(TestCase):
    def test_with_submodules(self):
        self.assertEqual(
            "//third_party/python:numpy",
            third_party_import_to_plz_target(
                "numpy.random",
                os.path.join("third_party", "python"),
            ),
        )
        return

    def test_with_only_top_level_lib_name(self):
        self.assertEqual(
            "//third_party/python:numpy",
            third_party_import_to_plz_target(
                "numpy",
                os.path.join("third_party", "python"),
            ),
        )
        return
