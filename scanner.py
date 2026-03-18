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
                        f"строка {line_num}, {start}-{i}"  # позиция всех пробелов
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
                        code = KEYWORDS[word] #CASE ENUM  
                    else:
                        code = 3 #IDENT

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
                            3, # ident
                            CODS_TYPES[3],
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

                # Неизвестный символ
                results.append([
                    'ERROR',
                    'invalid symbol',
                    char,
                    f"строка {line_num}, {start}"
                ])
                i += 1

        return results
