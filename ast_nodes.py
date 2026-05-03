"""Узлы абстрактного синтаксического дерева для грамматики enum."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AstNode:
    """Базовый узел AST: тип, дочерние узлы и атрибуты (имя, тип, значение и т.д.)."""

    node_type: str
    children: List[AstNode] = field(default_factory=list)
    attrs: Dict[str, Any] = field(default_factory=dict)


def format_ast_tree(root: AstNode) -> str:
    """Текстовое представление дерева (как в примере к лабораторной)."""

    lines: List[str] = [root.node_type]
    _append_children_lines(lines, root, "")
    return "\n".join(lines)


def _append_children_lines(lines: List[str], node: AstNode, prefix: str) -> None:
    items: List[tuple[str, Any]] = list(node.attrs.items())
    total = len(items) + len(node.children)

    for i, (key, val) in enumerate(items):
        is_last = i == total - 1
        branch = "└── " if is_last else "├── "
        lines.append(f"{prefix}{branch}{key}: {_format_attr(val)}")

    offset = len(items)
    for j, child in enumerate(node.children):
        i = offset + j
        is_last = i == total - 1
        branch = "└── " if is_last else "├── "
        ext = "    " if is_last else "│   "
        lines.append(f"{prefix}{branch}{child.node_type}")
        _append_children_lines(lines, child, prefix + ext)


def _format_attr(val: Any) -> str:
    if isinstance(val, str):
        return f'"{val}"'
    return str(val)
