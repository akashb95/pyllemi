from unittest import TestCase

from service.python_import.node_collector import NodeCollector


class TestNodesCollator(TestCase):
    @classmethod
    def setUp(cls):
        cls.collator = NodeCollector()

    def test_import_nodes(self):
        code = """
import numpy as np
import os.path
        """
        import_nodes = self.collator.collate_all(code=code)

        self.assertEqual(2, len(import_nodes))

        self.assertEqual(1, len(import_nodes[0].names))
        self.assertEqual("numpy", import_nodes[0].names[0].name)
        self.assertEqual("np", import_nodes[0].names[0].asname)

        self.assertEqual(1, len(import_nodes[1].names))
        self.assertEqual("os.path", import_nodes[1].names[0].name)
        self.assertEqual(None, import_nodes[1].names[0].asname)

        return

    def test_import_from_nodes(self):
        code = """
from numpy import random, potato
from .. import module1, module2
from ...pkg import module3, module4
        """

        import_nodes = self.collator.collate_all(code=code)

        self.assertEqual(3, len(import_nodes))

        self.assertEqual(0, import_nodes[0].level)
        self.assertEqual("numpy", import_nodes[0].module)
        self.assertEqual(2, len(import_nodes[0].names))
        self.assertEqual("random", import_nodes[0].names[0].name)
        self.assertEqual("potato", import_nodes[0].names[1].name)

        self.assertEqual(2, import_nodes[1].level)
        self.assertEqual(None, import_nodes[1].module)
        self.assertEqual(2, len(import_nodes[1].names))
        self.assertEqual("module1", import_nodes[1].names[0].name)
        self.assertEqual("module2", import_nodes[1].names[1].name)

        self.assertEqual(3, import_nodes[2].level)
        self.assertEqual("pkg", import_nodes[2].module)
        self.assertEqual(2, len(import_nodes[2].names))
        self.assertEqual("module3", import_nodes[2].names[0].name)
        self.assertEqual("module4", import_nodes[2].names[1].name)

        return

    def test_raises_syntax_error_with_invalid_py_code(self):
        code = """from .. import invalid.relative.import"""

        with self.assertRaises(SyntaxError):
            self.collator.collate_all(code=code)

        return
