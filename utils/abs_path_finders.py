import os
from typing import Iterable

# Root directory - platform-agnostic.
_ROOT_DIR = os.path.abspath(os.path.sep)


def to_project_root() -> str:
    """
    Finds the Please project root by looking for the .plzconfig file in parent dirs.
    """

    return _to_cwd_with_any_files({".plzconfig"})


def to_closest_build_pkg_dir(build_file_names: Iterable[str]) -> str:
    return _to_cwd_with_any_files(build_file_names)


def _to_cwd_with_any_files(filenames: Iterable[str]) -> str:
    """
    Returns the path which contains any one of the given filenames.
    """

    dir_to_check = os.getcwd()
    while len(dir_to_check) > 0:
        if dir_to_check == _ROOT_DIR:
            break

        for filename in filenames:
            if os.path.exists(os.path.join(dir_to_check, filename)):
                return dir_to_check

        dir_to_check = os.path.split(dir_to_check)[0]

    raise FileNotFoundError(
        f"could not find Please project root - failed to find files with any of names {{{', '.join(filenames)}}} "
        f"in parent directories to {dir_to_check}"
    )
