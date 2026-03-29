class LicensePlateAutomaton:
    def __init__(self):
        self.letters = set('АВСЕНКМОРТХУ')

        self.START = 0
        self.LETTER1 = 1
        self.DIGIT1 = 2
        self.DIGIT2 = 3
        self.DIGIT3 = 4
        self.LETTER2 = 5
        self.LETTER3 = 6
        self.REGION1 = 7
        self.REGION2 = 8
        self.REGION3 = 9

        self.reset()

    def reset(self):
        self.state = self.START
        self.current_match = []
        self.start_pos = 0

    def get_line_col(self, text, pos):
        line = text.count('\n', 0, pos) + 1
        line_start = text.rfind('\n', 0, pos) + 1
        col = pos - line_start + 1
        return line, col

    def add_match(self, text):
        if not self.current_match:
            return
        line, col = self.get_line_col(text, self.start_pos)
        self.matches.append({
            'substring': ''.join(self.current_match),
            'line': line,
            'start_pos': col,
            'end_pos': col + len(self.current_match) - 1,
            'length': len(self.current_match)
        })

    def try_start_new_match(self, char, pos, text):
        """Попытка начать новый номер с текущего символа"""
        if char in self.letters:
            self.state = self.LETTER1
            self.current_match = [char]
            self.start_pos = pos
        else:
            self.state = self.START

    def transition(self, char, pos, text):
        # S0: начало
        if self.state == self.START:
            if char in self.letters:
                self.state = self.LETTER1
                self.current_match = [char]
                self.start_pos = pos
            return

        # S1: первая буква → ждем цифру
        elif self.state == self.LETTER1:
            if char.isdigit():
                self.state = self.DIGIT1
                self.current_match.append(char)
            else:
                self.reset()
                self.try_start_new_match(char, pos, text)
            return

        # S2: первая цифра → ждем вторую
        elif self.state == self.DIGIT1:
            if char.isdigit():
                self.state = self.DIGIT2
                self.current_match.append(char)
            else:
                self.reset()
                self.try_start_new_match(char, pos, text)
            return

        # S3: вторая цифра → ждем третью
        elif self.state == self.DIGIT2:
            if char.isdigit():
                self.state = self.DIGIT3
                self.current_match.append(char)
            else:
                self.reset()
                self.try_start_new_match(char, pos, text)
            return

        # S4: третья цифра (проверка номера)
        elif self.state == self.DIGIT3:
            number = ''.join(self.current_match[-3:])
            if number == '000':
                self.reset()
                self.try_start_new_match(char, pos, text)
                return

            if char in self.letters:
                self.state = self.LETTER2
                self.current_match.append(char)
            else:
                self.reset()
                self.try_start_new_match(char, pos, text)
            return

        # S5: первая буква серии → ждем вторую букву серии
        elif self.state == self.LETTER2:
            if char in self.letters:
                self.state = self.LETTER3
                self.current_match.append(char)
            else:
                self.reset()
                self.try_start_new_match(char, pos, text)
            return

        # S6: вторая буква серии → ждем первую цифру региона
        elif self.state == self.LETTER3:
            if char.isdigit():
                self.state = self.REGION1
                self.current_match.append(char)
            else:
                self.reset()
                self.try_start_new_match(char, pos, text)
            return

        # S7: первая цифра региона → ждем вторую
        elif self.state == self.REGION1:
            if char.isdigit():
                self.state = self.REGION2
                self.current_match.append(char)
            else:
                self.reset()
                self.try_start_new_match(char, pos, text)
            return

        # S8: вторая цифра региона
        elif self.state == self.REGION2:
            if char.isdigit():
                self.state = self.REGION3
                self.current_match.append(char)
            else:
                # Регион из 2 цифр
                region = ''.join(self.current_match[-2:])
                if region != '00':
                    self.add_match(text)
                self.reset()
                self.try_start_new_match(char, pos, text)
            return

        # S9: третья цифра региона
        elif self.state == self.REGION3:
            # Регион из 3 цифр
            region = ''.join(self.current_match[-3:])
            if region != '000':
                self.add_match(text)
            self.reset()
            self.try_start_new_match(char, pos, text)
            return

    def scan(self, text):
        self.reset()
        self.matches = []

        for i, char in enumerate(text):
            self.transition(char, i, text)

        # Проверка незавершенных совпадений в конце строки
        if self.state == self.REGION2:
            region = ''.join(self.current_match[-2:])
            if region != '00':
                self.add_match(text)
        elif self.state == self.REGION3:
            region = ''.join(self.current_match[-3:])
            if region != '000':
                self.add_match(text)

        return self.matches