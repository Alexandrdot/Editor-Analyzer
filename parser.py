from dataclasses import dataclass
import re
from typing import List, Optional


@dataclass
class Token:
    code: int
    lexeme: str
    line: int
    start: int
    end: int
    raw_position: str


class Parser:
    def __init__(self, scanner_tokens: List[list]):
        self.syntax_errors: List[dict] = []
        self.tokens: List[Token] = []
        self.pos = 0
        self.last_consumed: Optional[Token] = None
        self.last_line = 1
        self.terminal_missing_case_identifier = False
        self._prepare_tokens(scanner_tokens)

    def parse(self) -> List[dict]:
        self._parse_enum_declaration()
        return self.syntax_errors

    def _prepare_tokens(self, scanner_tokens: List[list]) -> None:
        for token in scanner_tokens:
            code, _, lexeme, position = token
            if code == 7 or code == "ERROR":
                continue

            line, start, end = self._parse_position(position)
            self.tokens.append(
                Token(
                    code=int(code),
                    lexeme=lexeme,
                    line=line,
                    start=start,
                    end=end,
                    raw_position=position,
                )
            )
            self.last_line = line

    def _parse_position(self, position: str) -> tuple[int, int, int]:
        # format: "СЃС‚СЂРѕРєР° 2, 5-9" (locale-independent by parsing digits)
        nums = re.findall(r"\d+", position)
        if len(nums) >= 3:
            return int(nums[0]), int(nums[1]), int(nums[2])
        raise ValueError(f"Invalid token position: {position}")

    def _current(self) -> Optional[Token]:
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def _at_end(self) -> bool:
        return self._current() is None

    def _check(self, code: int) -> bool:
        current = self._current()
        return current is not None and current.code == code

    def _advance(self) -> Optional[Token]:
        current = self._current()
        if current is not None:
            self.pos += 1
            self.last_consumed = current
        return current

    def _consume(self, code: int) -> bool:
        if self._check(code):
            self._advance()
            return True
        return False

    def _error_location(self, prefer_eof_on_newline: bool = True) -> tuple[str, str]:
        current = self._current()

        if current is None:
            return self._eof_fragment_and_position()

        if (
            prefer_eof_on_newline
            and self.last_consumed is not None
            and current.line > self.last_consumed.line
        ):
            return self._eof_fragment_and_position()

        return current.lexeme, current.raw_position

    def _eof_fragment_and_position(self) -> tuple[str, str]:
        if self.last_consumed is not None:
            return "EOF", f"Строка {self.last_consumed.line}, EOF"
        return "EOF", f"Строка {self.last_line}, EOF"

    def _add_error(self, expected: str, prefer_eof_on_newline: bool = True) -> None:
        fragment, position = self._error_location(
            prefer_eof_on_newline=prefer_eof_on_newline
        )
        self.syntax_errors.append(
            {
                "fragment": fragment,
                "description": f"Ожидалось {expected}",
                "position": position,
            }
        )

    def _expect(self, code: int, expected: str) -> bool:
        if self._consume(code):
            return True

        self._add_error(expected, prefer_eof_on_newline=True)
        return False

    def _is_cascade_after_missing_case_identifier(self) -> bool:
        if not self.syntax_errors:
            return False
        last_error = self.syntax_errors[-1]
        if last_error.get("fragment") != "EOF":
            return False
        return "Ожидалось идентификатор" in last_error.get("description", "")

    def _parse_enum_declaration(self) -> None:
        # enum IDENT { CaseDecl+ } ;
        if not self._expect(1, "ключевое слово enum"):
            if self._check(3) and (self.pos + 1) < len(self.tokens):
                self._advance()
            else:
                return

        ident_ok = self._expect(3, "идентификатор")
        # Если после enum нет идентификатора и сразу не начинается блок,
        # это фатальная ошибка верхнего уровня (без каскада).
        if not ident_ok and not self._check(5):
            return

        has_open_brace = self._expect(5, "{")
        if not has_open_brace:
            return

        block_start_pos = self.pos
        has_case = self._parse_case_list()
        consumed_inside_block = self.pos > block_start_pos

        if has_open_brace:
            if self._at_end():
                if (
                    has_case or consumed_inside_block
                ) and not self.terminal_missing_case_identifier:
                    self._add_error("}")
                return

            self._expect(6, "}")
            self._expect(4, ";")
            return

    def _parse_case_list(self) -> bool:
        # CaseDecl+
        if not self._check(2):
            self._recover_missing_case_decl()
            self._parse_case_list_tail()
            return False

        self._parse_case_decl()
        self._parse_case_list_tail()
        return True

    def _parse_case_list_tail(self) -> None:
        if self._at_end() or self._check(6):
            return


        # Лишняя ';' внутри блока: дальше внешний уровень сообщит про ожидаемую '}'.
        if self._check(4):
            return

        if self._check(2):
            self._parse_case_decl()
            self._parse_case_list_tail()
            return

        self._recover_missing_case_decl()
        self._parse_case_list_tail()

    def _recover_missing_case_decl(self) -> None:
        # Восстановление для записи вида "ident ;" без ключевого слова case.
        self._add_error("Ожидалось ключевое case", prefer_eof_on_newline=False)
        if self._check(3):
            self._advance()
            self._expect(4, ";")
            return
        self._skip_to_case_boundary()

    def _skip_to_case_boundary(self) -> None:
        # Пропускаем мусор до начала следующего case, закрывающей скобки
        # или конца текущего проблемного объявления.
        while not self._at_end():
            if self._check(2) or self._check(6):
                return
            if self._check(4):
                self._advance()
                return
            self._advance()

    def _parse_case_decl(self) -> None:
        self._expect(2, "ключевое слово case")
        ident_ok = self._expect(3, "идентификатор")

        # Если идентификатор пропущен, не добавляем каскадную ошибку про ';',
        # но при наличии ';' потребляем его для восстановления.
        if not ident_ok:
            if self._at_end():
                self.terminal_missing_case_identifier = True
            self._consume(4)
            return

        self._expect(4, ";")
