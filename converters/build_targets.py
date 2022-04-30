import os
from functools import lru_cache
from typing import Any

import adapters.plz_query_graph as plz_adapter
from utils.path_finders import is_subpackage, to_closest_build_pkg_dir


def third_party_import_to_plz_target(
    py_abs_import: str,
    python_third_party_pkg_dir: str,
) -> str:
    return (
        f"//{python_third_party_pkg_dir.removeprefix(os.path.sep)}"
        f":{get_top_level_module_name(py_abs_import)}"
    )


def get_top_level_module_name(abs_import_path: str) -> str:
    return abs_import_path.split(".", maxsplit=1)[0] if "." in abs_import_path else abs_import_path


@lru_cache(128)
def get_build_graph_for_closest_pkg_dir(
    py_absolute_import: str,
    *,
    cwd: str,
) -> dict[str, Any]:
    import_path_stack = py_absolute_import.split(".")
    if not is_subpackage(os.path.abspath(*import_path_stack)):
        import_path_stack.pop()

    closest_parent_pkg_dir = to_closest_build_pkg_dir(os.path.abspath(*import_path_stack))

    return plz_adapter.get_plz_build_graph(
        pkg_dir=closest_parent_pkg_dir.removeprefix(cwd),
        args=["-i", "py"],
    )
