import re
from typing import Optional


class InvalidPlzTargetError(ValueError):
    pass


class PlzTarget:
    __absolute_target_path_pattern__ = re.compile(r"^//([\w/\-]*):(\w+)$")
    __simple_absolute_target_path_pattern__ = re.compile(r"^//([\w/\-]+)$")
    __relative_target_path_pattern__ = re.compile(r"^:([\w\-]+)")

    def __init__(self, target: str):
        absolute_target_match = re.match(self.__absolute_target_path_pattern__, target)
        if absolute_target_match is not None:
            self.build_pkg_dir: str = absolute_target_match.group(1)
            self.target_name: str = (
                absolute_target_match.group(2)
                if absolute_target_match.group(2) != ""
                else self.build_pkg_dir.split("/")[-1]
            )
            return

        simple_absolute_target_match = re.match(
            self.__simple_absolute_target_path_pattern__,
            target,
        )
        if simple_absolute_target_match is not None:
            self.build_pkg_dir: str = simple_absolute_target_match.group(1)
            self.target_name: str = self.build_pkg_dir.split("/")[-1]
            return

        relative_target_match = re.match(self.__relative_target_path_pattern__, target)
        if relative_target_match is not None:
            self.build_pkg_dir: str = ""
            self.target_name: str = relative_target_match.group(1)

        else:
            raise InvalidPlzTargetError(f"{target} does not match the format of a BUILD target path")

    def __eq__(self, other: "PlzTarget") -> bool:
        return self.canonicalise() == other.canonicalise()

    def __hash__(self):
        return hash(self.canonicalise())

    def __str__(self):
        return self.simplify()

    def with_tag(self, tag: str) -> str:
        return f"//{self.build_pkg_dir}:_{self.target_name}#{tag}"

    def canonicalise(self) -> str:
        return f"//{self.build_pkg_dir}:{self.target_name}"

    def simplify(self, relative_path_from_reporoot: Optional[str] = None) -> str:
        """
        Simplifies the plz target according to Plz Target conventions.
        I.e. //path/to/lib:lib ≡ //path/to/lib
        """

        if relative_path_from_reporoot is not None and self.build_pkg_dir == relative_path_from_reporoot:
            return f":{self.target_name}"

        build_pkg_dir_split = self.build_pkg_dir.split("/")
        build_pkg_dir_basename: str = ""
        if len(build_pkg_dir_split) > 0:
            build_pkg_dir_basename = build_pkg_dir_split[-1]

        if build_pkg_dir_basename == self.target_name:
            return f"//{self.build_pkg_dir}"

        return f"//{self.build_pkg_dir}:{self.target_name}"
