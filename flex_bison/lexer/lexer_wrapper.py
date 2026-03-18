from PyQt6.QtCore import QProcess


class FlexLexer:
    def __init__(self, lexer_path="./lexer"):
        self.lexer_path = lexer_path

    def scan(self, text):
        process = QProcess()
        process.start(self.lexer_path)
        process.waitForStarted()

        # Пишем текст напрямую
        process.write(text.encode('utf-8'))
        process.closeWriteChannel()

        process.waitForFinished(5000)
        output = process.readAllStandardOutput().data().decode('utf-8')
        tokens = []

        for line in output.strip().split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) == 4:
                    tokens.append([(parts[0]), parts[1], parts[2], parts[3]])
        return tokens
