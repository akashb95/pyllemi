import ast
import os.path
from dataclasses import dataclass
from typing import Collection, Iterator

from imports.common import IMPORT_NODE_TYPE
from imports.py_import import Import, ImportType, resolve_import_type


@dataclass
class ToAbsoluteImports:
    # Only required for computing absolute import paths from relative imports
    abs_path_to_project_root: str
    python_moduledir: str

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

    def transform_all(self, nodes: Collection[IMPORT_NODE_TYPE], *, pyfile_path: str = "") -> list[Import]:
        imports: list[Import] = []
        for node in nodes:
            for import_path in self.transform(node, pyfile_path=pyfile_path):
                imports.extend(import_path)

        return imports

    def _import_node(self, node: ast.Import) -> list[Import]:
        import_paths = []
        for alias in node.names:
            # TODO: use self._resolve_import_from_import_path_candidate
            import_path = alias.name

            import_type = resolve_import_type(alias.name, self.python_moduledir)
            if import_type == ImportType.THIRD_PARTY_MODULE:
                import_path = import_path.removeprefix(f"{self.python_moduledir}.").split(".", maxsplit=1)[0]

            import_paths.append(Import(import_path, import_type))
        return import_paths

    def _import_from_node(self, node: ast.ImportFrom, pyfile_path: str = "") -> list[Import]:
        if node.level > 0 and pyfile_path == "":
            # Cannot compute absolute import path from relative import path
            # if path of Python module is not provided.
            raise ValueError("pyfile_path cannot be empty for relative imports")

        imports: list[Import] = []
        if node.level > 0:
            raise NotImplementedError
            # transformed_ast_node = self._relative_import_from_node_to_absolute_import_from_node(node, pyfile_path)
            # for node in transformed_ast_node:
            #     imports.extend(self._import_from_node(node, pyfile_path))

        # from <> import <>
        for name in node.names:
            module_only_import = self._resolve_import_from_import_path_candidate(node.module)
            if module_only_import.type_ != ImportType.PACKAGE:
                imports.append(module_only_import)
                continue

            # Ascertain import type of `<node.module>.<name.name>`.
            full_import = self._resolve_import_from_import_path_candidate(f"{node.module}.{name.name}")
            if full_import.type_ != ImportType.UNKNOWN:
                imports.append(full_import)
                continue

            # Since we know node.module is a package, <node.module>.<name.name> must either be:
            # * import from __init__.py or __init__.pyi
            # * erroneous
            # TODO: add unit-test for this path
            init_import = self._resolve_import_from_import_path_candidate(f"{node.module}.__init__")
            if init_import.type_ == ImportType.MODULE or init_import.type_ == ImportType.STUB:
                imports.append(init_import)
                continue

            # Deal with the erroneous case by simply ignoring it -- the Python interpreter would complain about
            # not finding that import anyway.

        return imports

    def _relative_import_from_node_to_absolute_import_from_node(
            self,
            node: ast.ImportFrom,
            pyfile_path: str,
    ) -> list[ast.ImportFrom]:
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
            raise ImportError("attempted relative import beyond top-level package")

        relative_import_pkg = (  # noqa: F841
            relative_import_dir
                .removeprefix(self.abs_path_to_project_root)
                .replace(os.path.sep, ".")
        )

        if node.module is None:
            if relative_import_pkg == "":
                return [ast.ImportFrom(module=name, names=["__init__"], level=0) for name in node.names]

            # TODO: add unit-test for this path
            return [ast.ImportFrom(module=relative_import_pkg, names=node.names, level=0)]

        return [
            ast.ImportFrom(
                module=f"{relative_import_pkg}.{node.module}".removeprefix("."),
                names=node.names,
                level=0,
            ),
        ]

    def _resolve_import_from_import_path_candidate(self, import_path_candidate: str) -> Import:
        import_type = resolve_import_type(import_path_candidate, self.python_moduledir)

        if import_type == ImportType.THIRD_PARTY_MODULE:
            return Import(
                # Because we know it's a third-party module, only return the top-level module name.
                # E.g. `import third_party.python3.numpy.random.x` becomes simply `numpy`.
                import_path_candidate.removeprefix(f"{self.python_moduledir}.").split(".", maxsplit=1)[0],
                import_type,
            )

        if import_type == ImportType.UNKNOWN or import_type == ImportType.MODULE or import_type == ImportType.STUB:
            return Import(import_path_candidate, import_type)

        return Import(import_path_candidate, ImportType.PACKAGE)
