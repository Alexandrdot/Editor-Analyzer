from cods import CODS_TYPES, SYMBOLS, TYPES, KEYWORDS


class Scanner:
    def scan(self, text: str):
        """Построчный анализ с определением позиций"""
        results = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            i = 0
            length = len(line)

            while i < length:
                char = line[i]
                start = i + 1

                # Пробелы и табуляцию пропускаем
                if char in [' ', '\t']:
                    i += 1
                    continue

                # Комментарии // - пропускаем всю строку
                if char == '/' and i + 1 < length and line[i + 1] == '/':
                    break

                # Одиночные символы (: ; , = { })
                if char in SYMBOLS:
                    code = SYMBOLS[char]
                    results.append([
                        code,
                        CODS_TYPES[code],
                        char,
                        f"строка {line_num}, {start}-{start}"
                    ])
                    i += 1
                    continue

                # Строки в кавычках
                if char == '"':
                    string = ''
                    i += 1

                    while i < length and line[i] != '"':
                        string += line[i]
                        i += 1

                    if i < length and line[i] == '"':
                        i += 1
                        results.append([
                            16,
                            CODS_TYPES[16],
                            f'"{string}"',
                            f"строка {line_num}, {start}-{i}"
                        ])
                    else:
                        results.append([
                            'ERROR',
                            'unclosed string',
                            f'"{string}',
                            f"строка {line_num}, {start}-{i}"
                        ])
                        i += 1
                    continue

                # Слова и идентификаторы
                if char.isalpha():
                    word = ''
                    while i < length and (line[i].isalnum() or line[i] == '_'):
                        word += line[i]
                        i += 1

                    if word in KEYWORDS:
                        code = KEYWORDS[word]
                    elif word in TYPES:
                        code = TYPES[word]
                    else:
                        code = 8

                    results.append([
                        code,
                        CODS_TYPES[code],
                        word,
                        f"строка {line_num}, {start}-{i}"
                    ])
                    continue

                # Подчеркивание
                if char == '_':
                    underscores = ''
                    while i < length and line[i] == '_':
                        underscores += line[i]
                        i += 1

                    if i < length and (line[i].isalnum()):
                        word = underscores
                        while i < length and (line[i].isalnum() or line[i] == '_'):
                            word += line[i]
                            i += 1
                        results.append([
                            8,
                            CODS_TYPES[8],
                            word,
                            f"строка {line_num}, {start}-{i}"
                        ])
                    else:
                        results.append([
                            'ERROR',
                            'invalid symbol (only underscores)',
                            underscores,
                            f"строка {line_num}, {start}-{i}"
                        ])
                    continue

                # Числа
                if char.isdigit():
                    number = ''
                    has_dot = False
                    valid_number = True
                    start_number = start
                    raw_number = ''

                    while i < length and (line[i].isdigit() or line[i] == '.' or line[i] == '_'):
                        raw_number += line[i]
                        if line[i] == '_':
                            i += 1
                            continue
                        if line[i] == '.':
                            if has_dot:
                                valid_number = False
                                i += 1
                                while i < length and (line[i].isdigit() or line[i] == '.' or line[i] == '_'):
                                    raw_number += line[i]
                                    i += 1
                                break
                            has_dot = True
                        number += line[i]
                        i += 1

                    if not valid_number:
                        results.append([
                            'ERROR',
                            'invalid number (multiple dots)',
                            raw_number,
                            f"строка {line_num}, {start_number}-{i}"
                        ])
                    else:
                        code = 18 if has_dot else 17
                        results.append([
                            code,
                            CODS_TYPES[code],
                            number,
                            f"строка {line_num}, {start}-{i}"
                        ])
                    continue

                # Неизвестный символ
                results.append([
                    'ERROR',
                    'invalid symbol',
                    char,
                    f"строка {line_num}, {start}"
                ])
                i += 1

        return results
