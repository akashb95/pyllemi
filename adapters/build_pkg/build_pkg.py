from domain.build_files.build_file import BUILDFile


class BUILDPkg:
    """
    This class is used to manage BUILD targets in the given BUILD package.
    Where necessary, it will create new packages in the given path, and add new targets to it.
    Where appropriate, it will modify existing BUILD targets.

    It will provide representations of the BUILD targets which are contained in the package
    """
