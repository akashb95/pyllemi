from collections import namedtuple
from unittest import TestCase

from common.trie.trie import Node, Trie, new_trie, longest_existing_path_in_trie


class TestTrie(TestCase):
    def test_node_equality(self):
        SubTest = namedtuple("SubTest", ["name", "node_1", "node_2", "equal"])
        subtests = [
            SubTest(
                name="no children",
                node_1=Node(value="value", children=[]),
                node_2=Node(value="value", children=[]),
                equal=True,
            ),
            SubTest(
                name="equal children",
                node_1=Node(value="value", children=[Node(value="potato", children=[])]),
                node_2=Node(value="value", children=[Node(value="potato", children=[])]),
                equal=True,
            ),
            SubTest(
                name="unequal values no children",
                node_1=Node(value="value", children=[]),
                node_2=Node(value="another_value", children=[]),
                equal=False,
            ),
            SubTest(
                name="unequal children",
                node_1=Node(value="value", children=[Node(value="potato", children=[])]),
                node_2=Node(value="value", children=[Node(value="tomato", children=[])]),
                equal=False,
            ),
            SubTest(
                name="deep trie unequal children",
                node_1=Node(
                    value="value",
                    children=[
                        Node(value="potato", children=[Node("culprit", [])]),
                        Node(value="pot-ah-to", children=[]),
                    ],
                ),
                node_2=Node(
                    value="value",
                    children=[
                        Node(value="potato", children=[]),
                        Node(value="pot-ah-to", children=[Node("culprit", [])]),
                    ],
                ),
                equal=False,
            ),
            SubTest(
                name="deep trie unequal children",
                node_1=Node(
                    value="value",
                    children=[
                        Node(value="potato", children=[Node("culprit", [])]),
                        Node(value="pot-ah-to", children=[]),
                    ],
                ),
                node_2=Node(
                    value="value",
                    children=[
                        Node(value="potato", children=[Node("culprit", [])]),
                        Node(value="pot-ah-to", children=[]),
                    ],
                ),
                equal=True,
            ),
        ]

        for subtest in subtests:
            with self.subTest(subtest.name):
                if subtest.equal:
                    self.assertEqual(subtest.node_1, subtest.node_2)
                else:
                    self.assertNotEqual(subtest.node_1, subtest.node_2)

        return

    def test_trie_equality(self):
        SubTest = namedtuple("SubTest", ["name", "trie_1", "trie_2", "equal"])
        subtests = [
            SubTest(
                name="empty equal",
                trie_1=Trie([]),
                trie_2=Trie([]),
                equal=True,
            ),
            SubTest(
                name="equal 1 level deep",
                trie_1=Trie([Node(value="value", children=[])]),
                trie_2=Trie([Node(value="value", children=[])]),
                equal=True,
            ),
            SubTest(
                name="equal multiple root nodes",
                trie_1=Trie([Node(value="value", children=[]), Node("value_2", [])]),
                trie_2=Trie([Node(value="value", children=[]), Node("value_2", [])]),
                equal=True,
            ),
        ]

        for subtest in subtests:
            with self.subTest(subtest.name):
                if subtest.equal:
                    self.assertEqual(subtest.trie_1, subtest.trie_2)
                else:
                    self.assertNotEqual(subtest.trie_1, subtest.trie_2)

        return

    def test_new_trie_with_no_operands(self):
        self.assertEqual(
            Trie([]),
            new_trie([]),
        )
        return

    def test_new(self):
        operands = [
            "google.protobuf",
            "google",
            "this.is.a.really.long.one",
            "this.is.a.really.long.two",
            "this.is.a.really.long.one",  # deliberate duplicate
        ]

        trie = new_trie(operands)

        expected_trie = Trie(
            [
                Node(
                    "google",
                    [
                        Node(
                            "protobuf",
                            [
                                Node(None, []),
                            ],
                        ),
                        Node(None, []),
                    ],
                ),
                Node(
                    "this",
                    [
                        Node(
                            "is",
                            [
                                Node(
                                    "a",
                                    [
                                        Node(
                                            "really",
                                            [
                                                Node(
                                                    "long",
                                                    [
                                                        Node(
                                                            "one",
                                                            [
                                                                Node(None, []),
                                                            ],
                                                        ),
                                                        Node(
                                                            "two",
                                                            [
                                                                Node(None, []),
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                )
                            ],
                        )
                    ],
                ),
            ]
        )

        self.assertEqual(expected_trie, trie)
        return

    def test_is_in_trie(self):
        trie = new_trie(["google.protobuf", "google", "sklearn"])

        with self.subTest("exists with depth > 1"):
            self.assertIn("google.protobuf", trie)
        with self.subTest("exists with depth = 1"):
            self.assertIn("google", trie)
            self.assertIn("sklearn", trie)
        with self.subTest("does not contain"):
            self.assertNotIn("random", trie)

        with self.subTest("contains empty string (zero-value)"):
            self.assertIn("", trie)
        return

    def test_longest_existing_path_in_trie(self):
        trie = new_trie(["google.protobuf", "sklearn"])

        SubTest = namedtuple("SubTest", ["name", "operand", "expected_output"])

        subtests = [
            SubTest(
                name="empty operand",
                operand="",
                expected_output="",
            ),
            SubTest(
                name="operand with empty match",
                operand="sklearnx",
                expected_output="",
            ),
            SubTest(
                name="operand with exact match",
                operand="google.protobuf",
                expected_output="google.protobuf",
            ),
            SubTest(
                name="operand longer than match",
                operand="google.protobuf.field_mask_pb2",
                expected_output="google.protobuf",
            ),
            SubTest(
                name="operand shorter than any possible match",
                operand="google",
                expected_output="",
            ),
        ]

        for subtest in subtests:
            with self.subTest(subtest.name):
                self.assertEqual(
                    subtest.expected_output,
                    longest_existing_path_in_trie(trie, subtest.operand),
                )
