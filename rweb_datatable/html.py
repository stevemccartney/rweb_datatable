import operator
from typing import Dict, Union, Type


class Flag:
    pass


def render_attributes(attributes: Dict[str, Union[str, Type[Flag]]]):
    out = []
    for name, value in attributes.items():
        if value is Flag:
            out.append(name)
        else:
            out.append(f'{name}="{value}"')
    return " ".join(out)


class Node:
    def __init__(
        self,
        name: str,
        *children: Union[str, "Node"],
        is_self_closing: bool = False,
        attributes: Dict[str, str] = None,
    ):
        self.name = name
        self.is_self_closing = is_self_closing
        self.attributes = attributes or {}
        self.children = children or []

    def __add__(self, other):
        operator.iadd(self, other)
        return self

    def __iadd__(self, node: Union[str, "Node"]):
        self.children.append(node)
        return self

    def __str__(self) -> str:
        attributes = render_attributes(self.attributes)
        spacer = " " if attributes else ""
        if self.is_self_closing:
            return f"<{self.name}{spacer}{attributes}>"
        else:
            children = "".join([str(child) for child in self.children])
            return f"<{self.name}{spacer}{attributes}>{children}</{self.name}>"

    def __repr__(self) -> str:
        return f"<Node {self.name}>"

    def node(
        self,
        name: str,
        *children: Union[str, "Node"],
        attributes: Dict[str, Union[str, bool, int, float]] = None,
        is_self_closing: bool = False,
    ) -> "Node":
        node = Node(name, *children, attributes=attributes or {}, is_self_closing=is_self_closing)
        self.children.append(node)
        return node
