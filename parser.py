class Parser:
    def __init__(self):
        self.tokens = []
        self.pos = 0
        self.errors = []
        self.current_token = None

        # FOLLOW множества для метода Айронса
        self.follow = {
            'EnumDecl': {1, None},
            'EnumBody': {1, None},
            'CaseList': {6},
            'Case': {2, 6},
            'Identifier': {4, 5, 6, 2, 1}
        }

    def parse(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

        if not tokens:
            self.errors.append({
                'fragment': '',
                'line': 1,
                'start_pos': 1,
                'end_pos': 1,
                'message': 'Пустой входной текст'
            })
            return self.errors

        while self.current():
            self.enum_decl()

        return self.errors

    def _get_line(self, token):
        return int(token[3].replace('строка ', '').split(',')[0])

    def _get_start_pos(self, token):
        return int(token[3].split(',')[1].strip().split('-')[0])

    def _get_end_pos(self, token):
        return int(token[3].split(',')[1].strip().split('-')[1])

    def current(self):
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if token[0] != 7:
                self.current_token = token
                return self.current_token
            self.pos += 1
        self.current_token = None
        return None

    def next(self):
        self.pos += 1
        return self.current()

    def match(self, expected_code):
        token = self.current()
        if not token:
            return False

        if token[0] == expected_code:
            self.next()
            return True
        return False

    def irons_recovery(self, follow_set):
        if not follow_set:
            return
        while self.current():
            if self.current()[0] in follow_set:
                return
            self.next()

    def enum_decl(self):
        """<EnumDecl> → enum <Identifier> { <CaseList> } ;"""

        has_case = False

        # 1. Ожидаем 'enum'
        if not self.match(1):
            token = self.current()
            if token:
                self.errors.append({
                    'fragment': token[2],
                    'line': self._get_line(token),
                    'start_pos': self._get_start_pos(token),
                    'end_pos': self._get_end_pos(token),
                    'message': 'Ожидалось ключевое слово enum'
                })
                self.irons_recovery(self.follow['EnumDecl'])
                return

        # 2. Ожидаем идентификатор (имя enum)
        if not self.match(3):
            token = self.current()
            if token:
                self.errors.append({
                    'fragment': token[2],
                    'line': self._get_line(token),
                    'start_pos': self._get_start_pos(token),
                    'end_pos': self._get_end_pos(token),
                    'message': 'Отсутствие идентификатора после enum'
                })
                self.irons_recovery(self.follow['Identifier'])

        # 3. Ожидаем '{'
        if not self.match(5):
            token = self.current()
            if token:
                self.errors.append({
                    'fragment': token[2],
                    'line': self._get_line(token),
                    'start_pos': self._get_start_pos(token),
                    'end_pos': self._get_end_pos(token),
                    'message': 'Отсутствие { после идентификатора enum'
                })
                self.irons_recovery(self.follow['EnumBody'])
                return

        # 4. Разбираем список case
        has_case = self.case_list()

        # 5. Проверяем, что был хотя бы один case
        if not has_case:
            token = self.current()
            if token:
                self.errors.append({
                    'fragment': token[2] if token else '',
                    'line': self._get_line(token) if token else 1,
                    'start_pos': self._get_start_pos(token) if token else 1,
                    'end_pos': self._get_end_pos(token) if token else 1,
                    'message': 'Ожидалось ключевое слово case'
                })

        # 6. Ожидаем '}'
        if not self.match(6):
            token = self.current()
            if token:
                self.errors.append({
                    'fragment': token[2],
                    'line': self._get_line(token),
                    'start_pos': self._get_start_pos(token),
                    'end_pos': self._get_end_pos(token),
                    'message': 'Отсутствие } в конце'
                })
            else:
                last_token = self.tokens[-1] if self.tokens else None
                self.errors.append({
                    'fragment': '',
                    'line': self._get_line(last_token) if last_token else 1,
                    'start_pos': self._get_start_pos(last_token) if last_token else 1,
                    'end_pos': self._get_end_pos(last_token) if last_token else 1,
                    'message': 'Отсутствие } в конце'
                })
            return

        # 7. Ожидаем ';' после } (обязательно!)
        if not self.match(4):
            token = self.current()
            if token:
                self.errors.append({
                    'fragment': token[2],
                    'line': self._get_line(token),
                    'start_pos': self._get_start_pos(token),
                    'end_pos': self._get_end_pos(token),
                    'message': 'Отсутствие ; после } в конце'
                })
            else:
                last_token = self.tokens[-1] if self.tokens else None
                self.errors.append({
                    'fragment': '',
                    'line': self._get_line(last_token) if last_token else 1,
                    'start_pos': self._get_start_pos(last_token) if last_token else 1,
                    'end_pos': self._get_end_pos(last_token) if last_token else 1,
                    'message': 'Отсутствие ; после } в конце'
                })

    def case_list(self):
        """<CaseList> → <Case> | <Case> <CaseList>
           Возвращает True если был хотя бы один case"""
        has_case = False
        while self.current():
            token = self.current()

            if token[0] == 6:  # }
                break

            if token[0] == 2:  # case
                self.case_item()
                has_case = True
            elif token[0] == 3:  # identifier без case
                # Идентификатор без case - ошибка
                self.errors.append({
                    'fragment': token[2],
                    'line': self._get_line(token),
                    'start_pos': self._get_start_pos(token),
                    'end_pos': self._get_end_pos(token),
                    'message': 'Ожидалось ключевое слово case перед идентификатором'
                })
                self.next()  # пропускаем идентификатор
                # Если есть ;, пропускаем его
                if self.current() and self.current()[0] == 4:
                    self.next()
            else:
                # Другой токен - ошибка
                self.errors.append({
                    'fragment': token[2],
                    'line': self._get_line(token),
                    'start_pos': self._get_start_pos(token),
                    'end_pos': self._get_end_pos(token),
                    'message': 'Ожидалось ключевое слово case'
                })
                self.next()

        return has_case

    def case_item(self):
        """<Case> → case <Identifier> ;"""

        # 1. Пропускаем 'case'
        if not self.match(2):
            return

        # 2. Ожидаем идентификатор
        if not self.match(3):
            token = self.current()
            if token:
                self.errors.append({
                    'fragment': token[2],
                    'line': self._get_line(token),
                    'start_pos': self._get_start_pos(token),
                    'end_pos': self._get_end_pos(token),
                    'message': 'Отсутствие идентификатора после case'
                })
                self.irons_recovery(self.follow['Case'])
                return

        # 3. Ожидаем ';'
        if not self.match(4):
            token = self.current()
            if token:
                self.errors.append({
                    'fragment': token[2],
                    'line': self._get_line(token),
                    'start_pos': self._get_start_pos(token),
                    'end_pos': self._get_end_pos(token),
                    'message': 'Отсутствие ; после идентификатора case'
                })