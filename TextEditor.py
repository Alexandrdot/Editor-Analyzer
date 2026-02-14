from PyQt6.QtWidgets import (QMainWindow, QTextEdit,
                             QTabWidget, QFileDialog, QMessageBox,)
from PyQt6.uic import loadUi
from PyQt6.QtGui import QAction
import os


class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('design.ui', self)

        self.setup_actions()

        self.tabWidgetEditor = self.findChild(QTabWidget, 'tabWidgetEditor')
        self.tabWidgetEditor.setTabsClosable(True)
        self.tabWidgetEditor.tabCloseRequested.connect(self.close_tab)

        self.file_paths = {}

    def setup_actions(self):
        self.openFile = self.findChild(QAction, 'open')
        if self.openFile:
            self.openFile.triggered.connect(self.open_file)

        self.createFile = self.findChild(QAction, 'create')
        if self.createFile:
            self.createFile.triggered.connect(self.new_file)

        self.saveFile = self.findChild(QAction, 'save')
        if self.saveFile:
            self.saveFile.triggered.connect(self.save_file)

        self.saveAsFile = self.findChild(QAction, 'saveAs')
        if self.saveAsFile:
            self.saveAsFile.triggered.connect(self.save_file_as)

        self.exitFile = self.findChild(QAction, 'exit')
        if self.exitFile:
            self.exitFile.triggered.connect(self.close)

    def close_tab(self, index):
        widget = self.tabWidgetEditor.widget(index)

        if widget.document().isModified():
            reply = QMessageBox.question(
                self,
                "Несохраненные изменения",
                "Сохранить изменения перед закрытием?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self.tabWidgetEditor.setCurrentIndex(index)
                self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        if id(widget) in self.file_paths:
            del self.file_paths[id(widget)]

        self.tabWidgetEditor.removeTab(index)
        widget.deleteLater()

    def open_file(self):
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self,
            "Выберите файл для открытия",
            "",
            "*.*"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                file_name = os.path.basename(file_path)
                self.create_new_tab(file_name, content, file_path)
                self.statusBar().showMessage(
                    f"Файл {file_name} успешно открыт", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось открыть файл:\n{str(e)}")

    def create_new_tab(self, title="Новый документ", content="",
                       file_path=None):
        text_edit = QTextEdit()
        text_edit.setPlainText(content)

        index = self.tabWidgetEditor.addTab(text_edit, title)

        if file_path:
            self.file_paths[id(text_edit)] = file_path

        self.tabWidgetEditor.setCurrentIndex(index)

        return text_edit

    def new_file(self):
        self.create_new_tab()
        self.statusBar().showMessage("Новый документ создан", 2000)

    def save_file(self):
        text_edit = self.tabWidgetEditor.currentWidget()

        if not text_edit:
            return

        file_path = self.file_paths.get(id(text_edit))

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(text_edit.toPlainText())

                self.statusBar().showMessage(
                    f"Файл{os.path.basename(file_path)} сохранен", 2000)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось сохранить файл: {str(e)}")
        else:
            self.save_file_as()

    def save_file_as(self):
        text_edit = self.tabWidgetEditor.currentWidget()

        if not text_edit:
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл как",
                                                   "",
                                                   "Текстовые файлы (*.txt);;"
                                                   "rtf (*.rtf);;"
                                                   "Все файлы (*.*)")

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(text_edit.toPlainText())

                    self.file_paths[id(text_edit)] = file_path

                    index = self.tabWidgetEditor.currentIndex()
                    file_name = os.path.basename(file_path)
                    self.tabWidgetEditor.setTabText(index, file_name)

                    self.statusBar().showMessage(
                        f"Файл сохранен как {file_name}", 3000)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось сохранить файл: {str(e)}")
