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
        # File
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
            self.exitFile.triggered.connect(self.close_program)

        # Edit
        self.backModified = self.findChild(QAction, 'back')
        if self.backModified:
            self.backModified.triggered.connect(lambda: self.edit_file('back'))

        self.forwardModified = self.findChild(QAction, 'forward')
        if self.forwardModified:
            self.forwardModified.triggered.connect(lambda: self.edit_file('forward'))

        self.cutText = self.findChild(QAction, 'cut')
        if self.cutText:
            self.cutText.triggered.connect(lambda: self.edit_file('cut'))

        self.copyText = self.findChild(QAction, 'copy')
        if self.copyText:
            self.copyText.triggered.connect(lambda: self.edit_file('copy'))

        self.pasteText = self.findChild(QAction, 'paste')
        if self.pasteText:
            self.pasteText.triggered.connect(lambda: self.edit_file('paste'))

        self.deleteText = self.findChild(QAction, 'deleteFile')
        if self.deleteText:
            self.deleteText.triggered.connect(lambda: self.edit_file('delete'))

        self.selectAllText = self.findChild(QAction, 'selectAll')
        if self.selectAllText:
            self.selectAllText.triggered.connect(lambda: self.edit_file('selectAll'))

        # Info
        self.aboutProgram = self.findChild(QAction, 'about')
        if self.aboutProgram:
            self.aboutProgram.triggered.connect(self.about_program)

        self.infoDoc = self.findChild(QAction, 'info')
        if self.infoDoc:
            self.infoDoc.triggered.connect(self.info_doc)

    def close_program(self):
        # Проверяем все открытые вкладки
        unsaved_tabs = []
        for i in range(self.tabWidgetEditor.count()):
            widget = self.tabWidgetEditor.widget(i)
            if widget.document().isModified():
                unsaved_tabs.append(i)

        if unsaved_tabs:
            reply = QMessageBox.question(
                self,
                "Несохраненные изменения",
                f"Есть несохраненные изменения в {len(unsaved_tabs)} файле(ах).\n"
                "Сохранить все перед выходом?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Сохраняем все измененные файлы
                for i in unsaved_tabs:
                    self.tabWidgetEditor.setCurrentIndex(i)
                    result = self.save_file()
                    if result == "cancelled":
                        cont = QMessageBox.question(
                            self,
                            "Сохранение отменено",
                            "Вы отменили сохранение файла. Продолжить выход без сохранения?",
                            QMessageBox.StandardButton.Yes |
                            QMessageBox.StandardButton.No
                        )
                        if cont == QMessageBox.StandardButton.No:
                            return

                    elif result == "error":
                        cont = QMessageBox.question(
                            self,
                            "Ошибка сохранения",
                            "Не удалось сохранить файл. Продолжить выход?",
                            QMessageBox.StandardButton.Yes |
                            QMessageBox.StandardButton.No
                        )
                        if cont == QMessageBox.StandardButton.No:
                            return

            elif reply == QMessageBox.StandardButton.Cancel:
                return
        self.close()

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
                saved = self.save_file()
                if not saved:
                    return
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
                text_edit.document().setModified(False)
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
                    text_edit.document().setModified(False)
                    index = self.tabWidgetEditor.currentIndex()
                    file_name = os.path.basename(file_path)
                    self.tabWidgetEditor.setTabText(index, file_name)

                    self.statusBar().showMessage(
                        f"Файл сохранен как {file_name}", 3000)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось сохранить файл: {str(e)}")

    def edit_file(self, action):

        text_edit = self.tabWidgetEditor.currentWidget()

        if not text_edit:
            return

        if action == 'back':
            if text_edit.document().isUndoAvailable():
                text_edit.undo()
                self.statusBar().showMessage("Отмена действия", 1500)
            else:
                self.statusBar().showMessage("Нечего отменять", 1500)

        elif action == 'forward':
            if text_edit.document().isRedoAvailable():
                text_edit.redo()
                self.statusBar().showMessage("Повтор действия", 1500)
            else:
                self.statusBar().showMessage("Нечего повторять", 1500)

        elif action == 'cut':
            if text_edit.textCursor().hasSelection():
                text_edit.cut()
                self.statusBar().showMessage("Текст вырезан", 1500)
            else:
                self.statusBar().showMessage("Нет выделенного текста", 1500)

        elif action == 'copy':
            if text_edit.textCursor().hasSelection():
                text_edit.copy()
                self.statusBar().showMessage("Текст скопирован", 1500)
            else:
                self.statusBar().showMessage("Нет выделенного текста", 1500)

        elif action == 'paste':
            text_edit.paste()
            self.statusBar().showMessage("Текст вставлен", 1500)

        elif action == 'delete':
            if text_edit.textCursor().hasSelection():
                cursor = text_edit.textCursor()
                cursor.removeSelectedText()
                self.statusBar().showMessage("Текст удален", 1500)
            else:
                self.statusBar().showMessage("Нет выделенного текста", 1500)

        elif action == 'selectAll':
            text_edit.selectAll()
            self.statusBar().showMessage("Весь текст выделен", 1500)

    def about_program(self):
        about_text = """
        <h2>Текстовый редактор</h2>
        <p>Версия 0.1 (Beta Release)</p>
        <p>Программа для редактирования текстовых файлов</p>
        <p>© 2026 Все права защищены</p>
        <p>Разработано с использованием PyQt6</p>
        """

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("О программе")
        msg_box.setText(about_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def info_doc(self):
        info_text = """
        <h2>Руководство пользователя</h2>

        <h3>Основные функции:</h3>
        <ul>
            <li><b>Файл → Создать</b> - создать новый документ</li>
            <li><b>Файл → Открыть</b> - открыть существующий файл</li>
            <li><b>Файл → Сохранить</b> - сохранить текущий файл</li>
            <li><b>Файл → Сохранить как</b> - сохранить файл под новым именем</li>
        </ul>

        <h3>Редактирование:</h3>
        <ul>
            <li><b>Правка → Отменить/Повторить</b> - отмена/повтор действий</li>
            <li><b>Правка → Вырезать/Копировать/Вставить</b> - работа с буфером обмена</li>
            <li><b>Правка → Выделить всё</b> - выделить весь текст</li>
        </ul>

        <h3>Горячие клавиши:</h3>
        <ul>
            <li>Ctrl+N - Новый файл</li>
            <li>Ctrl+O - Открыть файл</li>
            <li>Ctrl+S - Сохранить</li>
            <li>Ctrl+Z - Отменить</li>
            <li>Ctrl+Y - Повторить</li>
        </ul>
        """

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Руководство пользователя")
        msg_box.setText(info_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def closeEvent(self, event):
        result = self.close_program()

        if result is False:
            event.ignore()
        else:
            event.accept()
