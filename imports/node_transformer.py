import ast
import os.path
from dataclasses import dataclass
from typing import Collection, Iterator

from imports.common import IMPORT_NODE_TYPE
from imports.py_import import Import, ImportType, resolve_import_type
from utils.path_finders import is_module, is_subpackage
from converters.paths import (
    convert_py_import_path_to_os_path,
    convert_os_path_to_import_path,
)


@dataclass
class ToAbsoluteImports:
    # Only required for computing absolute import paths from relative imports
    abs_path_to_project_root: str

    def transform(self, node: IMPORT_NODE_TYPE, *, pyfile_path: str = "") -> Iterator[list[Import]]:
        if isinstance(node, ast.Import):
            yield self._import_node(node)

        elif isinstance(node, ast.ImportFrom):
            try:
                yield self._import_from_node(node, pyfile_path)
            except ValueError as e:
                raise ValueError(f"could not transform import(s): {node.names} - {e}")

        # TODO: add support for __import__ function calls

        else:
            raise TypeError(
                f"can only transform nodes of type Import and ImportFrom; got {type(node).__name__}"
            )

    def transform_all(self, nodes: Collection[IMPORT_NODE_TYPE]) -> list[Import]:
        import_paths: list[Import] = []
        for node in nodes:
            for import_path in self.transform(node):
                import_paths.extend(import_path)

        return import_paths

    @staticmethod
    def _import_node(node: ast.Import) -> list[Import]:
        import_paths = []
        for alias in node.names:
            import_paths.append(Import(alias.name, resolve_import_type(alias.name)))
        return import_paths

    def _import_from_node(self, node: ast.ImportFrom, pyfile_path: str = "") -> list[Import]:
        if node.level > 0 and pyfile_path == "":
            # Cannot compute absolute import path from relative import path
            # if path of Python module is not provided.
            raise ValueError("pyfile_path cannot be empty for relative imports")

        if node.level > 0:
            return self._relative_import(node, pyfile_path)

        # from <> import <>
        import_paths: list[Import] = []
        for name in node.names:
            import_type = resolve_import_type(node.module)

            if import_type == ImportType.UNKNOWN:
                # If import is:
                # * Erroneous; or
                # * Is a 3rd-party module import; or
                # * Is a builtin module import.
                import_paths.append(Import(node.module, import_type))
                continue

            if import_type == ImportType.MODULE:
                import_paths.append(Import(node.module, ImportType.MODULE))
                continue

            # At this point, the node.module must lead to a package.
            # Ascertain import type of `package.name`.
            full_import = ".".join([node.module, name.name])
            full_import_type = resolve_import_type(full_import)
            import_paths.append(Import(full_import, full_import_type))

        return import_paths

    def _relative_import(self, node: ast.ImportFrom, pyfile_path: str) -> list[Import]:
        relative_import_dir = os.path.abspath(
            os.path.join(
                # Find absolute path to containing package.
                os.path.dirname(os.path.abspath(pyfile_path)),
                # Each '.' in a relative import refers to the containing package of the Py file.
                *[".."] * (node.level - 1),
            )
        )

        if relative_import_dir.find(self.abs_path_to_project_root) == -1:
            # ensure level isn't so high that the relative import dir is outside the project root
            raise ImportError("relative import moves out of project root")

        # TODO: implement
        relative_import_pkg = (  # noqa: F841
            os.path.splitext(relative_import_dir)[0]
                .removeprefix(self.abs_path_to_project_root)
                .lstrip(os.path.sep)
                .replace(os.path.sep, ".")
        )

        # from . import <>
        # TODO

        # from .<> import <>
        # TODO

        raise NotImplementedError
