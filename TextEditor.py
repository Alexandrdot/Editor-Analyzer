from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QMenuBar, QFileDialog,
                             QMessageBox, QLabel)
from PyQt6.Qsci import (QsciScintilla, QsciLexerPython, QsciLexerCPP,
                        QsciLexerJava, QsciLexerHTML, QsciLexerJavaScript)
from PyQt6.QtGui import QAction, QColor, QDesktopServices
from PyQt6.QtCore import QUrl
from PyQt6.uic import loadUi
import os
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


class SimpleCodeEditor(QsciScintilla):
    def __init__(self, language="python"):
        super().__init__()

        # Нумерация строк
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setMarginsForegroundColor(QColor("#e0e0e0"))
        self.setMarginsBackgroundColor(QColor("#2d2d2d"))
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
        self.set_lexer(language)

    def set_lexer(self, language):
        lexers = {
            "python": QsciLexerPython,
            "cpp": QsciLexerCPP,
            "java": QsciLexerJava,
            "html": QsciLexerHTML,
            "javascript": QsciLexerJavaScript,
        }

        if language in lexers:
            lexer = lexers[language]()
            lexer.setDefaultPaper(QColor("#1e1e1e"))
            lexer.setPaper(QColor("#1e1e1e"))
            lexer.setDefaultColor(QColor("#d4d4d4"))

            if language == "python":
                lexer.setColor(QColor("#569CD6"), QsciLexerPython.Keyword)
                lexer.setColor(QColor("#4EC9B0"), QsciLexerPython.ClassName)
                lexer.setColor(QColor("#DCDCAA"), QsciLexerPython.FunctionMethodName)
                lexer.setColor(QColor("#9CDCFE"), QsciLexerPython.Number)
                lexer.setColor(QColor("#6A9955"), QsciLexerPython.Comment)
                lexer.setColor(QColor("#D4D4D4"), QsciLexerPython.Operator)
                lexer.setColor(QColor("#DCDCAA"), QsciLexerPython.Decorator)

            elif language in ["cpp", "java", "javascript"]:
                lexer.setColor(QColor("#569CD6"), 0)  # Keywords
                lexer.setColor(QColor("#4EC9B0"), 1)  # Types
                lexer.setColor(QColor("#CE9178"), 2)  # Strings
                lexer.setColor(QColor("#6A9955"), 3)  # Comments

            self.setLexer(lexer)

    def wheelEvent(self, event):
        if event.modifiers():
            if event.angleDelta().y() > 0:
                self.zoomIn(1)
            else:
                self.zoomOut(1)
            self.setMarginsFont(self.font())
        else:
            super().wheelEvent(event)


class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = resource_path('design.ui')
        loadUi(ui_path, self)

        # Словарь с переводами для статусбара
        self.status_msgs = {
            'ru': {
                'opened': "Файл {} успешно открыт",
                'created': "Новый документ создан",
                'saved': "Файл {} сохранен",
                'saved_as': "Файл сохранен как {}",
                'undo': "Отмена действия",
                'undo_unavail': "Нечего отменять",
                'redo': "Повтор действия",
                'redo_unavail': "Нечего повторять",
                'cut': "Текст вырезан",
                'cut_unavail': "Нет выделенного текста",
                'copy': "Текст скопирован",
                'copy_unavail': "Нет выделенного текста",
                'paste': "Текст вставлен",
                'delete': "Текст удален",
                'delete_unavail': "Нет выделенного текста",
                'select_all': "Весь текст выделен",
                'lang_switched': "Язык переключен на Русский",
            },
            'en': {
                'opened': "File {} successfully opened",
                'created': "New document created",
                'saved': "File {} saved",
                'saved_as': "File saved as {}",
                'undo': "Undo action",
                'undo_unavail': "Nothing to undo",
                'redo': "Redo action",
                'redo_unavail': "Nothing to redo",
                'cut': "Text cut",
                'cut_unavail': "No text selected",
                'copy': "Text copied",
                'copy_unavail': "No text selected",
                'paste': "Text pasted",
                'delete': "Text deleted",
                'delete_unavail': "No text selected",
                'select_all': "All text selected",
                'lang_switched': "Language switched to English",
            }
        }

        self.setup_actions()
        self.current_lang = 'ru'
        self.set_russian()

        self.tabWidgetEditor = self.findChild(QTabWidget, 'tabWidgetEditor')
        self.menubar = self.findChild(QMenuBar, 'menubar')
        self.label_texteditor = self.findChild(QLabel, 'label_texteditor')
        self.label_result = self.findChild(QLabel, 'label_result')
        self.tabWidgetEditor.setTabsClosable(True)
        self.tabWidgetEditor.tabCloseRequested.connect(self.close_tab)
        self.setAcceptDrops(True)
        self.file_paths = {}

        self.label_texteditor.linkActivated.connect(self.open_link)
        self.label_result.linkActivated.connect(self.open_link)

    def tr(self, key, *args):
        msg = self.status_msgs[self.current_lang].get(key, key)
        return msg.format(*args) if args else msg

    def open_link(self, url):
        QDesktopServices.openUrl(QUrl(url))

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
            self.forwardModified.triggered.connect(lambda:
                                                   self.edit_file('forward'))

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
            self.selectAllText.triggered.connect(lambda:
                                                 self.edit_file('selectAll'))

        # Info
        self.aboutProgram = self.findChild(QAction, 'about')
        if self.aboutProgram:
            self.aboutProgram.triggered.connect(self.about_program)

        self.infoDoc = self.findChild(QAction, 'info')
        if self.infoDoc:
            self.infoDoc.triggered.connect(self.info_doc)

        self.translate = self.findChild(QAction, 'translate')
        if self.translate:
            self.translate.triggered.connect(self.translate_text)

    def close_program(self):
        # Проверяем все открытые вкладки
        unsaved_tabs = []
        for i in range(self.tabWidgetEditor.count()):
            widget = self.tabWidgetEditor.widget(i)
            if widget.isModified():
                unsaved_tabs.append(i)

        if unsaved_tabs:
            reply = QMessageBox.question(
                self,
                "Несохраненные изменения",
                f"Есть несохраненные изменения в {len(
                    unsaved_tabs)} файле(ах).\n"
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
                            "Вы отменили сохранение. Продолжить выход?",
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

        if widget.isModified():
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
        file_path, _ = QFileDialog.getOpenFileName(
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
                self.statusBar().showMessage(self.tr('opened', file_name), 3000)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось открыть файл:\n{str(e)}")

    def create_new_tab(self, title="Новый документ", content="",
                       file_path=None):
        language = "python"  # по умолчанию
        if file_path:
            lang = self.get_language_from_filename(file_path)
            if lang:
                language = lang
        text_edit = SimpleCodeEditor(language)
        text_edit.setText(content)

        index = self.tabWidgetEditor.addTab(text_edit, title)

        if file_path:
            self.file_paths[id(text_edit)] = file_path
            text_edit.setModified(False)

        self.tabWidgetEditor.setCurrentIndex(index)

        return text_edit

    def get_language_from_filename(self, filename):
        ext = os.path.splitext(filename)[1].lower()

        language_map = {
            '.py': 'python',
            '.cpp': 'cpp', '.cxx': 'cpp', '.cc': 'cpp', '.h': 'cpp',
            '.hpp': 'cpp',
            '.java': 'java',
            '.html': 'html', '.htm': 'html',
            '.js': 'javascript',
            '.txt': None,
        }
        return language_map.get(ext, None)

    def new_file(self):
        self.create_new_tab()
        self.statusBar().showMessage(self.tr('created'), 2000)

    def save_file(self):
        text_edit = self.tabWidgetEditor.currentWidget()

        if not text_edit:
            return

        file_path = self.file_paths.get(id(text_edit))

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(text_edit.text())

                text_edit.setModified(False)
                self.statusBar().showMessage(
                    self.tr('saved', os.path.basename(file_path)), 2000)

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
                    file.write(text_edit.text())
                    self.file_paths[id(text_edit)] = file_path
                    text_edit.setModified(False)
                    index = self.tabWidgetEditor.currentIndex()
                    file_name = os.path.basename(file_path)
                    self.tabWidgetEditor.setTabText(index, file_name)

                    self.statusBar().showMessage(
                        self.tr('saved_as', file_name), 3000)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось сохранить файл: {str(e)}")

    def edit_file(self, action):
        text_edit = self.tabWidgetEditor.currentWidget()

        if not text_edit:
            return

        if action == 'back':
            if text_edit.isUndoAvailable():
                text_edit.undo()
                self.statusBar().showMessage(self.tr('undo'), 1500)
            else:
                self.statusBar().showMessage(self.tr('undo_unavail'), 1500)

        elif action == 'forward':
            if text_edit.isRedoAvailable():
                text_edit.redo()
                self.statusBar().showMessage(self.tr('redo'), 1500)
            else:
                self.statusBar().showMessage(self.tr('redo_unavail'), 1500)

        elif action == 'cut':
            if text_edit.hasSelectedText():
                text_edit.cut()
                self.statusBar().showMessage(self.tr('cut'), 1500)
            else:
                self.statusBar().showMessage(self.tr('cut_unavail'), 1500)

        elif action == 'copy':
            if text_edit.hasSelectedText():
                text_edit.copy()
                self.statusBar().showMessage(self.tr('copy'), 1500)
            else:
                self.statusBar().showMessage(self.tr('copy_unavail'), 1500)

        elif action == 'paste':
            text_edit.paste()
            self.statusBar().showMessage(self.tr('paste'), 1500)

        elif action == 'delete':
            if text_edit.hasSelectedText():
                text_edit.removeSelectedText()
                self.statusBar().showMessage(self.tr('delete'), 1500)
            else:
                self.statusBar().showMessage(self.tr('delete_unavail'), 1500)

        elif action == 'selectAll':
            text_edit.selectAll()
            self.statusBar().showMessage(self.tr('select_all'), 1500)

    def about_program(self):
        msg_box = QMessageBox(self)
        if self.current_lang == 'en':
            msg_box.setWindowTitle("About")
            text = self.about_text
        else:
            msg_box.setWindowTitle("О программе")
            text = self.about_text

        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def info_doc(self):
        msg_box = QMessageBox(self)
        if self.current_lang == 'en':
            msg_box.setWindowTitle("User Guide")
            text = self.info_text
        else:
            msg_box.setWindowTitle("Руководство пользователя")
            text = self.info_text

        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def closeEvent(self, event):
        self.close_program()
        event.accept()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path and os.path.isfile(file_path):
                self.open_file_path(file_path)

    def open_file_path(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.create_new_tab(
                os.path.basename(file_path), content, file_path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def translate_text(self):
        # Переключаем язык
        if self.current_lang == 'ru':
            self.set_english()
            self.current_lang = 'en'
            self.statusBar().showMessage(self.tr('lang_switched'), 3000)
        else:
            self.set_russian()
            self.current_lang = 'ru'
            self.statusBar().showMessage(self.tr('lang_switched'), 3000)

    def set_russian(self):
        # Меню Файл
        self.openFile.setText("Открыть")
        self.createFile.setText("Создать")
        self.saveFile.setText("Сохранить")
        self.saveAsFile.setText("Сохранить как...")
        self.exitFile.setText("Выход")

        # Меню Правка
        self.backModified.setText("Отменить")
        self.forwardModified.setText("Повторить")
        self.cutText.setText("Вырезать")
        self.copyText.setText("Копировать")
        self.pasteText.setText("Вставить")
        self.deleteText.setText("Удалить")
        self.selectAllText.setText("Выделить всё")

        # Меню Инфо
        self.aboutProgram.setText("О программе")
        self.infoDoc.setText("Руководство")

        actions = self.menubar.actions()

        actions[0].setText("Файл")
        actions[1].setText("Правка")
        actions[2].setText("Текст")
        actions[3].setText("Пуск")
        actions[4].setText("Справка")

        self.label_texteditor.setText("Текстовой редактор:")
        self.label_result.setText("Результаты:")

        self.update_tab_titles('ru')
        self.update_dialog_texts('ru')

    def set_english(self):
        # File menu
        self.openFile.setText("Open")
        self.createFile.setText("New")
        self.saveFile.setText("Save")
        self.saveAsFile.setText("Save As...")
        self.exitFile.setText("Exit")

        # Edit menu
        self.backModified.setText("Undo")
        self.forwardModified.setText("Redo")
        self.cutText.setText("Cut")
        self.copyText.setText("Copy")
        self.pasteText.setText("Paste")
        self.deleteText.setText("Delete")
        self.selectAllText.setText("Select All")

        # Info menu
        self.aboutProgram.setText("About")
        self.infoDoc.setText("Help")

        actions = self.menubar.actions()

        actions[0].setText("File")
        actions[1].setText("Edit")
        actions[2].setText("Text")
        actions[3].setText("Play")
        actions[4].setText("Info")

        self.label_texteditor.setText("Text Editor:")
        self.label_result.setText("Results:")

        self.update_tab_titles('en')
        self.update_dialog_texts('en')

    def update_tab_titles(self, lang):
        for i in range(self.tabWidgetEditor.count()):
            widget = self.tabWidgetEditor.widget(i)
            current_text = self.tabWidgetEditor.tabText(i)
            base_text = current_text.replace("*", "")

            if base_text in ["Новый документ", "New Document"]:
                new_text = "Новый документ" if lang == 'ru' else "New Document"
                if widget.isModified():
                    new_text += "*"
                self.tabWidgetEditor.setTabText(i, new_text)

    def update_dialog_texts(self, lang):
        if lang == 'ru':
            self.about_text = """
            <h2>Текстовый редактор</h2>
            <p>Версия 0.1 (Beta Release)</p>
            <p>Программа для редактирования текстовых файлов</p>
            <p>© 2026 Все права защищены</p>
            <p>Разработано с использованием PyQt6</p>
            """

            self.info_text = """
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
            <h3>
                <a href="https://github.com/Alexandrdot/Editor-Analyzer/blob/main/docs/ru/manual.md">Нажмите, для получения подробного руководства</a>
            </h3>
            """
        else:
            self.about_text = """
            <h2>Text Editor</h2>
            <p>Version 0.1 (Beta Release)</p>
            <p>Program for editing text files</p>
            <p>© 2026 All rights reserved</p>
            <p>Developed with PyQt6</p>
            """

            self.info_text = """
            <h2>User Guide</h2>
            <h3>Main Functions:</h3>
            <ul>
                <li><b>File → New</b> - create new document</li>
                <li><b>File → Open</b> - open existing file</li>
                <li><b>File → Save</b> - save current file</li>
                <li><b>File → Save As...</b> - save file with new name</li>
            </ul>
            <h3>Editing:</h3>
            <ul>
                <li><b>Edit → Undo/Redo</b> - undo/redo actions</li>
                <li><b>Edit → Cut/Copy/Paste</b> - clipboard operations</li>
                <li><b>Edit → Select All</b> - select all text</li>
            </ul>
            <h3>Hotkeys:</h3>
            <ul>
                <li>Ctrl+N - New file</li>
                <li>Ctrl+O - Open file</li>
                <li>Ctrl+S - Save</li>
                <li>Ctrl+Z - Undo</li>
                <li>Ctrl+Y - Redo</li>
            </ul>
            <h3>
                <a href="https://github.com/Alexandrdot/Editor-Analyzer/blob/main/docs/en/manual.md">Click here for a detailed guide.</a>
            </h3>
            """
