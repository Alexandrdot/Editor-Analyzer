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
                'errors': []
            }
        
        # Читаем stdout и stderr
        output = process.readAllStandardOutput().data().decode('utf-8')
        error_output = process.readAllStandardError().data().decode('utf-8')
        
        os.unlink(temp_file)
        
        # Собираем все ошибки
        errors = []
        success = False
        
        # Сначала проверяем stderr (там могут быть отладочные сообщения)
        for line in error_output.split('\n'):
            if 'DEBUG:' in line:
                print(line)
        
        # Парсим stdout
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('SUCCESS|'):
                success = True
            elif line.startswith('ERROR|'):
                # Формат: ERROR|фрагмент|строка X, позиция Y|сообщение
                parts = line.split('|')
                if len(parts) >= 4:
                    errors.append([
                        parts[1],        # фрагмент
                        parts[2],        # местоположение
                        parts[3]         # описание
                    ])
        
        return {
            'success': success,
            'errors': errors
        }