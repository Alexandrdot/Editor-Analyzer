from cods import CODS_TYPES, SYMBOLS, KEYWORDS


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

                # Пробелы и табуляцию - сохраняем как один токен
                if char in [' ', '\t']:
                    space_count = 0
                    while i < length and line[i] in [' ', '\t']:
                        space_count += 1
                        i += 1
                    results.append([
                        7,  # код пробела
                        CODS_TYPES[7],  # 'space'
                        ' ',  # один пробел в лексеме
                        f"строка {line_num}, {start}-{i}"  # позиция пробелов
                    ])
                    continue

                # Комментарии // - пропускаем всю строку
                if char == '/' and i + 1 < length and line[i + 1] == '/':
                    break

                # Одиночные символы (; { })
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

                # Слова и идентификаторы
                if char.isalpha():
                    word = ''
                    while i < length and (line[i].isalnum() or line[i] == '_'):
                        word += line[i]
                        i += 1

                    if word in KEYWORDS:
                        code = KEYWORDS[word]
                    else:
                        code = 3

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
                        while i < length and (line[i].isalnum() or
                                              line[i] == '_'):
                            word += line[i]
                            i += 1
                        results.append([
                            3,  # ident
                            CODS_TYPES[3],
                            word,
                            f"строка {line_num}, {start}-{i}"
                        ])
                    else:
                        # Ошибка: только подчеркивания
                        results.append([
                            'ERROR',
                            'invalid symbol (only underscores)',
                            underscores,
                            f"строка {line_num}, {start}-{i}"
                        ])
                    continue

                # Собираем все подряд идущие недопустимые символы
                invalid_chars = ''
                while i < length:
                    current_char = line[i]

                    # Проверяем, является ли текущий символ допустимым
                    is_valid = (
                        current_char in [' ', '\t'] or
                        current_char in SYMBOLS or
                        current_char.isalpha() or
                        current_char == '_' or
                        (current_char == '/' and i + 1 < length
                         and line[i + 1] == '/')
                    )

                    if is_valid:
                        break
                    invalid_chars += current_char
                    i += 1

                # Если собрали недопустимые символы - добавляем одну ошибку
                if invalid_chars:
                    end_pos = start + len(invalid_chars) - 1
                    results.append([
                        'ERROR',
                        'invalid symbol',
                        invalid_chars,  # вся группа недопустимых символов
                        f"строка {line_num}, {start}-{end_pos}"
                    ])

                # Продолжаем цикл (i уже увеличили в while)

        return results
