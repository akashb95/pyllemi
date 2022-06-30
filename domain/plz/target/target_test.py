from unittest import TestCase

from domain.plz.target.target import Target, InvalidPlzTargetError


class TestPlzTarget(TestCase):
    def test_invalid_target_pattern_raises_err(self):
        self.assertRaisesRegex(
            InvalidPlzTargetError,
            "potato does not match the format of a BUILD target path",
            Target,
            "potato",
        )
        return

    def test_with_target_at_reporoot(self):
        plz_target = Target("//:main")
        self.assertEqual("", plz_target.build_pkg_dir)
        self.assertEqual("main", plz_target.target_name)
        return

    def test_with_absolute_target_path_pattern(self):
        plz_target = Target("//path/to:target")
        self.assertEqual("path/to", plz_target.build_pkg_dir)
        self.assertEqual("target", plz_target.target_name)
        return

    def test_with_simple_absolute_target_path_pattern(self):
        plz_target = Target("//path/to")
        self.assertEqual("path/to", plz_target.build_pkg_dir)
        self.assertEqual("to", plz_target.target_name)
        return

    def test_with_relative_target_path_pattern(self):
        plz_target = Target("//:target")
        self.assertEqual("", plz_target.build_pkg_dir)
        self.assertEqual("target", plz_target.target_name)
        return

    def test_with_tag(self):
        plz_target = Target("//path/to:target")
        self.assertEqual(
            "//path/to:_target#tag",
            plz_target.with_tag("tag"),
        )
        return

    def test_canonicalize(self):
        plz_target = Target("//path/to/lib")
        self.assertEqual("//path/to/lib:lib", plz_target.canonicalise())
        return

    def test_simplify_when_absolute_target_path_is_simplest_possible(self):
        plz_target = Target("//path/to/lib:target")
        self.assertEqual(
            "//path/to/lib:target",
            plz_target.simplify(),
        )
        self.assertEqual("//path/to/lib:target", str(plz_target))
        return

    def test_simplify(self):
        plz_target = Target("//path/to/lib:lib")
        self.assertEqual(
            "//path/to/lib",
            plz_target.simplify(),
        )
        self.assertEqual("//path/to/lib", str(plz_target))
        return

    def test_simplify_with_relative_path_from_reporoot(self):
        plz_target = Target("//path/to/lib:lib")
        self.assertEqual(":lib", plz_target.simplify("path/to/lib"))
        return
