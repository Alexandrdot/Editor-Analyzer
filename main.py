from PyQt6.QtWidgets import QApplication
import sys
from TextEditor import TextEditor
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor


def set_dark_theme(app):
    """Принудительно устанавливает темную тему"""
    app.setStyle("Fusion")

    palette = QPalette()

    # Базовые цвета
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

    app.setPalette(palette)


# В main:
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Принудительно включаем темную тему
    set_dark_theme(app)

    window = TextEditor()
    window.show()
    sys.exit(app.exec())
