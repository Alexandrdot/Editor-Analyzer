"""Графическое отображение AST (PyQt6 Graphics View)."""

from __future__ import annotations

from typing import Dict, List, Tuple

from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QDialog,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QVBoxLayout,
)

from ast_nodes import AstNode

NODE_H = 52
NODE_MIN_W = 100
V_SPACE = 110
MARGIN = 40


def _node_caption(node: AstNode) -> str:
    parts = [node.node_type]
    if node.attrs:
        detail = ", ".join(f"{k}={v!r}" for k, v in node.attrs.items())
        parts.append(detail)
    return "\n".join(parts)


def _layout_positions(root: AstNode) -> Dict[int, Tuple[float, float]]:
    """Позиции центров узлов: x — порядок листьев, y — глубина."""

    positions: Dict[int, Tuple[float, float]] = {}

    class Counter:
        def __init__(self) -> None:
            self.x = 0.0

    def set_depth(n: AstNode, d: int) -> None:
        n._ast_depth = d  # type: ignore[attr-defined]
        for c in n.children:
            set_depth(c, d + 1)

    def assign_x(n: AstNode, xc: Counter) -> float:
        if not n.children:
            n._ast_x = xc.x  # type: ignore[attr-defined]
            xc.x += NODE_MIN_W + 36
            return n._ast_x  # type: ignore[attr-defined]
        xs = [assign_x(c, xc) for c in n.children]
        n._ast_x = sum(xs) / len(xs)  # type: ignore[attr-defined]
        return n._ast_x  # type: ignore[attr-defined]

    set_depth(root, 0)
    assign_x(root, Counter())

    def collect(n: AstNode) -> None:
        d = int(n._ast_depth)  # type: ignore[attr-defined]
        x = float(n._ast_x)  # type: ignore[attr-defined]
        y = MARGIN + d * V_SPACE
        positions[id(n)] = (x, y)
        for c in n.children:
            collect(c)

    collect(root)
    return positions


def _collect_edges(root: AstNode) -> List[Tuple[AstNode, AstNode]]:
    edges: List[Tuple[AstNode, AstNode]] = []

    def walk(n: AstNode) -> None:
        for c in n.children:
            edges.append((n, c))
            walk(c)

    walk(root)
    return edges


class AstGraphicsDialog(QDialog):
    def __init__(self, root: AstNode, title: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(920, 620)

        scene = QGraphicsScene(self)
        scene.setBackgroundBrush(QColor("#2b2b2b"))

        positions = _layout_positions(root)
        edges = _collect_edges(root)

        pen = QPen(QColor("#888888"))
        pen.setWidth(2)

        node_items: Dict[int, QGraphicsRectItem] = {}

        def draw_node(n: AstNode) -> None:
            cx, cy = positions[id(n)]
            caption = _node_caption(n)
            text = QGraphicsTextItem(caption)
            text.setDefaultTextColor(QColor("#e0e0e0"))
            f = QFont()
            f.setStyleHint(QFont.StyleHint.Monospace)
            f.setPointSize(10)
            text.setFont(f)
            br = text.boundingRect()
            w = max(NODE_MIN_W, br.width() + 24)
            h = max(NODE_H, br.height() + 16)
            rect = QGraphicsRectItem(cx - w / 2, cy - h / 2, w, h)
            rect.setBrush(QColor("#3c3c3c"))
            rect.setPen(QPen(QColor("#5a9fd4"), 2))
            text.setPos(cx - br.width() / 2, cy - br.height() / 2)
            scene.addItem(rect)
            scene.addItem(text)
            node_items[id(n)] = rect

        def walk_draw(n: AstNode) -> None:
            draw_node(n)
            for c in n.children:
                walk_draw(c)

        walk_draw(root)

        for parent, child in edges:
            pr = node_items[id(parent)]
            cr = node_items[id(child)]
            p1 = pr.mapToScene(
                pr.rect().center().x(), pr.rect().bottom()
            )
            p2 = cr.mapToScene(cr.rect().center().x(), cr.rect().top())
            line = QGraphicsLineItem(p1.x(), p1.y(), p2.x(), p2.y())
            line.setPen(pen)
            line.setZValue(-1)
            scene.addItem(line)

        view = QGraphicsView(scene)
        view.setRenderHints(
            view.renderHints()
            | QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
        )

        lay = QVBoxLayout(self)
        lay.addWidget(view)

        scene.setSceneRect(scene.itemsBoundingRect().adjusted(-40, -40, 40, 40))
