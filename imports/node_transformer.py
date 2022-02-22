import ast
import os.path
from dataclasses import dataclass
from typing import Collection, Iterator

from imports.common import (
    IMPORT_NODE_TYPE,
    is_module,
    is_subpackage,
)
from converters.converters import (
    convert_py_import_path_to_os_path,
    convert_os_path_to_import_path,
)


@dataclass
class ToAbsoluteImportPaths:
    abs_path_to_project_root: str  # Only required for computing absolute import paths from relative imports

    def transform(self, node: IMPORT_NODE_TYPE, *, pyfile_path: str = "") -> Iterator[list[str]]:
        if isinstance(node, ast.Import):
            yield self._import_node(node)

        elif isinstance(node, ast.ImportFrom):
            try:
                yield self._import_from_node(node, pyfile_path)
            except ValueError as e:
                raise ValueError(f"could not transform import(s): {node.names} - {e}")

        # TODO: add support for __import__ function calls

        else:
            raise TypeError(f"can only transform nodes of type Import and ImportFrom; got {type(node).__name__}")

    def transform_all(self, nodes: Collection[IMPORT_NODE_TYPE]) -> list[str]:
        import_paths: list[str] = []
        for node in nodes:
            for import_path in self.transform(node):
                import_paths.extend(import_path)

        return import_paths

    @staticmethod
    def _import_node(node: ast.Import) -> list[str]:
        import_paths = []
        for alias in node.names:
            import_paths.append(alias.name)
        return import_paths

    def _import_from_node(self, node: ast.ImportFrom, pyfile_path: str = "") -> list[str]:
        if node.level > 0 and pyfile_path == "":
            # Cannot compute absolute import path from relative import path if path of Python module is not provided.
            raise ValueError(f"pyfile_path cannot be empty for relative imports")

        if node.level > 0:
            return self._relative_import(node, pyfile_path)

        # from <> import <>
        import_paths: list[str] = []
        for name in node.names:
            # `from module_or_package import name`
            module_or_package = convert_py_import_path_to_os_path(node.module)

            if is_module(module := os.path.join(module_or_package, name.name + ".py")):
                import_paths.append(convert_os_path_to_import_path(module, self.abs_path_to_project_root))

            elif is_subpackage(subpackage := os.path.join(module_or_package, name.name)):
                import_paths.append(convert_os_path_to_import_path(subpackage, self.abs_path_to_project_root))

            elif is_subpackage(module_or_package) or is_module(module_or_package):
                # If `module_or_package` is a module or package, and `name` is an object.
                import_paths.append(node.module)

        return import_paths

    def _relative_import(self, node: ast.ImportFrom, pyfile_path: str) -> list[str]:
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

        relative_import_pkg = (
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
