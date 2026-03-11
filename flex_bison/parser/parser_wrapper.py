from PyQt6.QtCore import QProcess
import tempfile
import os

class BisonParser:
    def __init__(self, parser_path="./flex_bison/parser/parser"):
        self.parser_path = parser_path
        
    def parse(self, text):
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as f:
            f.write(text)
            temp_file = f.name
        
        process = QProcess()
        process.start(self.parser_path, [temp_file])
        
        if not process.waitForFinished(5000):
            os.unlink(temp_file)
            return {
                'success': False,
                'output': '',
                'errors': [['ERROR', 'timeout', 'Parser timeout']]
            }
        
        output = process.readAllStandardOutput().data().decode('utf-8')
        error_output = process.readAllStandardError().data().decode('utf-8')
        
        os.unlink(temp_file)
        
        # Парсим вывод
        errors = []
        for line in error_output.split('\n'):
            if line.strip():
                errors.append(['ERROR', 'syntax', line])
        
        success = (process.exitCode() == 0 and len(errors) == 0)
        
        return {
            'success': success,
            'output': output,
            'errors': errors
        }
