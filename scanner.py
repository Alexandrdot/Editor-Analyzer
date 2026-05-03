from cods import CODS_TYPES, ID, NUM, SPACE, SYMBOLS


class Scanner:
    def scan(self, text: str, lang: str = "ru"):
        """Построчный разбор: числа, идентификаторы, операции, скобки."""
        results = []
        lines = text.split("\n")
        invalid_msg = {
            "ru": "недопустимый символ",
            "en": "invalid character",
        }
        msg = invalid_msg.get(lang, invalid_msg["ru"])

        for line_num, line in enumerate(lines, 1):
            i = 0
            length = len(line)

            while i < length:
                char = line[i]
                start = i + 1

                if char in [" ", "\t", "\r"]:
                    while i < length and line[i] in [" ", "\t", "\r"]:
                        i += 1
                    results.append(
                        [
                            SPACE,
                            CODS_TYPES[SPACE],
                            " ",
                            f"строка {line_num}, {start}-{i}",
                        ]
                    )
                    continue

                if char in SYMBOLS:
                    code = SYMBOLS[char]
                    results.append(
                        [
                            code,
                            CODS_TYPES[code],
                            char,
                            f"строка {line_num}, {start}-{start}",
                        ]
                    )
                    i += 1
                    continue

                if char.isdigit():
                    word = ""
                    while i < length and line[i].isdigit():
                        word += line[i]
                        i += 1
                    results.append(
                        [
                            NUM,
                            CODS_TYPES[NUM],
                            word,
                            f"строка {line_num}, {start}-{i}",
                        ]
                    )
                    continue

                if char.isalpha():
                    word = ""
                    while i < length and (line[i].isalnum() or line[i] == "_"):
                        word += line[i]
                        i += 1
                    results.append(
                        [
                            ID,
                            CODS_TYPES[ID],
                            word,
                            f"строка {line_num}, {start}-{i}",
                        ]
                    )
                    continue

                invalid_chars = ""
                while i < length:
                    current_char = line[i]
                    is_valid = current_char in [" ", "\t", "\r"] or (
                        current_char in SYMBOLS
                    ) or current_char.isdigit() or current_char.isalpha()
                    if is_valid:
                        break
                    invalid_chars += current_char
                    i += 1

                if invalid_chars:
                    end_pos = start + len(invalid_chars) - 1
                    results.append(
                        [
                            "ERROR",
                            msg,
                            invalid_chars,
                            f"строка {line_num}, {start}-{end_pos}",
                        ]
                    )

        return results
