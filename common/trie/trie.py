from abc import ABC
from dataclasses import dataclass
from typing import Collection, TypeVar, Optional

_VT = TypeVar("_VT", bytes, str)

DEFAULT_SEP = "."


class BaseNode(ABC):
    pass


@dataclass
class Node(BaseNode):
    value: Optional[_VT]
    children: list["Node"]

    def __eq__(self, other: "Node") -> bool:
        return self.value == other.value and self.children == other.children

    def __str__(self) -> str:
        return f"{self.value} -> {[str(child.value) for child in self.children]}"


@dataclass
class Trie(BaseNode):
    children: list[Node]

    def __eq__(self, other: "Trie") -> bool:
        return self.children == other.children

    def __str__(self):
        return f"{[str(child) for child in self.children]}"

    def __contains__(self, item: _VT, sep: str = DEFAULT_SEP):
        return is_in_trie(self, operand=item, sep=sep)


def new_trie(operands: Collection[_VT], sep: _VT = DEFAULT_SEP) -> Trie:
    trie = Trie([])
    if not operands:
        return trie

    for operand in operands:
        children = trie.children
        candidate_node_values: list[_VT] = operand.split(sep)

        for candidate_node_value in candidate_node_values:
            # Find any child whose value matches the node_value.
            if (node := get_from_child_values(candidate_node_value, children)) is not None:
                # Value already exists - no need to add it as a new node to the trie.
                children = node.children
                continue

            children.append(new_node := Node(candidate_node_value, []))
            children = new_node.children

        if get_from_child_values(None, children) is not None:
            # This operand was a duplicate.
            continue
        children.append(Node(None, []))

    return trie


def get_from_child_values(value: Optional[_VT], children: list[Node]) -> Optional[Node]:
    # Find any child whose value matches the node_value.
    matches: list[Node] = list(filter(lambda child: child.value == value, children))
    if (num_matches := len(matches)) == 1:
        # Value already exists - no need to add it as a new node to the trie.
        return matches[0]
    elif num_matches > 1:
        # This indicates something is wrong with the implementation of the Trie construction.
        ValueError(f"found {num_matches} children with identical values")
    return None


def is_in_trie(trie: Trie, operand: _VT, sep: str = DEFAULT_SEP) -> bool:
    if not operand:
        return True
    candidate_node_values: list[_VT] = operand.split(sep)

    children = trie.children
    for candidate_node_value in candidate_node_values:
        if (node := get_from_child_values(candidate_node_value, children)) is None:
            return False

        children = node.children

    if get_from_child_values(None, children) is None:
        return False
    return True


def longest_existing_path_in_trie(trie: Trie, operand: _VT, sep: str = DEFAULT_SEP) -> str:
    if not operand:
        return ""

    candidate_node_values: list[_VT] = operand.split(sep)

    existing_path_values: list[_VT] = []
    unflushed: list[_VT] = []

    children = trie.children
    for candidate_node_value in candidate_node_values:
        if (node := get_from_child_values(candidate_node_value, children)) is not None:
            if get_from_child_values(None, node.children) is not None:
                # This is a complete output.
                unflushed.append(node.value)
                existing_path_values.extend(unflushed)
                unflushed.clear()
            else:
                # This is an incomplete output.
                unflushed.append(node.value)

            # Move onto next node.
            children = node.children
            continue

        # If candidate value is not found in the children, then longest existing path has already been found.
        break

    return sep.join(existing_path_values)
