import ast
from logging import DEBUG
from typing import Iterator, List

from common.logger.logger import setup_logger
from imports.common import IMPORT_NODE_TYPE


class NodesCollator:
    """
    Collates AST nodes responsible for imports from the given path.
    """

    def __init__(self):
        self._logger = setup_logger(name=__name__, level=DEBUG)
        return

    def collate(self, *, code: str, path: str = "") -> Iterator[IMPORT_NODE_TYPE]:
        try:
            root = ast.parse(code, path)
        except SyntaxError as e:
            if path != "":
                self._logger.error(f"could not parse Python code at {path}")
            else:
                self._logger.error("could not parse python code (check debug logs for code)")

            if path != "":
                self._logger.debug(path)
            self._logger.debug(code)
            raise e

        for node in ast.walk(root):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                yield node
            # TODO: parse __import__(...) function calls.

    def collate_all(self, *, code: str, path: str = "") -> List[IMPORT_NODE_TYPE]:
        import_nodes: List[IMPORT_NODE_TYPE] = []
        for node in self.collate(code=code, path=path):
            import_nodes.append(node)

        return import_nodes
