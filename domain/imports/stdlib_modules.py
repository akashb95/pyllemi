import importlib
import re
import sys
from functools import lru_cache
from typing import Optional, Union
from urllib.request import urlopen


def _scrape_standard_libs(py_version: Optional[str] = None, top_level_only: bool = True):
    """
    A hacky solution to scrape the Python standard libs for a Python version < 3.10.

    Since this solution could fail due to network errors, the generated files will be persisted
    in VCS. The function exists as a record of the code used to generate the aforementioned files.
    """

    if py_version is None:
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    url = f"https://docs.python.org/{py_version}/py-modindex.html"
    with urlopen(url) as f:
        page = f.read()
    modules = set()
    for module in re.findall(r'#module-(.*?)[\'"]', page.decode("ascii", "replace")):
        if top_level_only:
            module = module.split(".")[0]
        modules.add(module)
    return modules


@lru_cache(maxsize=1)
def get_stdlib_module_names(version: Optional[tuple[int, int]] = None) -> Union[frozenset[str], set[str]]:
    py_version = version
    if version is None:
        py_version = sys.version_info

    # Python >= 3.10 has an inbuilt method
    if py_version >= (3, 10):
        return sys.stdlib_module_names

    # Otherwise, use generated set of builtins.
    try:
        stdlib_pkg = importlib.import_module(f"imports.stdlib.{py_version.major}_{py_version.minor}")
    except ModuleNotFoundError:
        raise ValueError(f"could not fetch builtin modules for Python version {'.'.join(py_version)}")

    return getattr(stdlib_pkg, "MODULE_NAMES")


if __name__ == "__main__":
    import os

    VERSIONS = ("2.7", "3.5", "3.6", "3.7", "3.8", "3.9")

    os.makedirs("stdlib")
    for version in VERSIONS:
        with open(os.path.join("stdlib", version.replace(".", "_") + ".py"), "w") as f:
            f.write("# GENERATED FILE, DO NOT MODIFY\n")
            f.write(f"MODULE_NAMES = {_scrape_standard_libs(version)}\n")
