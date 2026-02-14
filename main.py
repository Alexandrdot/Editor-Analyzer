from PyQt6.QtWidgets import QApplication
import sys
from TextEditor import TextEditor


def main():
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
