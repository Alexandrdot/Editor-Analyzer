from dataclasses import dataclass
import re
from typing import List, Optional


ENUM = 1
CASE = 2
IDENTIFIER = 3
SEMICOLON = 4
LBRACE = 5
RBRACE = 6
SPACE = 7


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
        self._prepare_tokens(scanner_tokens)

    def parse(self) -> List[dict]:
        self._parse_program()
        return self.syntax_errors

    def _parse_program(self) -> None:
        # Program := EnumDecl*
        while not self._at_end():
            if self._check(ENUM):
                self._parse_enum_declaration()
                continue

            self._add_error("enum", prefer_eof_on_newline=False)

            # Recovery for "Name { ... };" where only enum is missing.
            if self._check(IDENTIFIER) and self._peek_code(1) == LBRACE:
                self._advance()
                self._advance()
                if self._parse_enum_body():
                    self._expect_declaration_semicolon()
                continue

            self._skip_to_next_enum()

    def _parse_enum_declaration(self) -> None:
        # EnumDecl := enum Identifier { CaseDecl+ } ;
        if not self._expect(ENUM, "ключевое слово enum", prefer_eof_on_newline=False):
            self._skip_to_next_enum()
            return

        if not self._consume(IDENTIFIER):
            self._add_error("идентификатор", prefer_eof_on_newline=False)

            # Recovery for "enum enum { ... }" or "enum case { ... }":
            # the keyword is a malformed enum name.
            if self._check(ENUM, CASE) and self._peek_code(1) == LBRACE:
                self._advance()

            if self._check(LBRACE):
                self._advance()
                if self._parse_enum_body():
                    self._expect_declaration_semicolon()
                return

            if self._starts_enum_body():
                if self._parse_enum_body():
                    self._expect_declaration_semicolon()
                return

            self._skip_to_next_enum()
            return

        if not self._expect(LBRACE, "{"):
            if self._starts_enum_body():
                if self._parse_enum_body():
                    self._expect_declaration_semicolon()
                return

            # If another enum starts here, keep it for the program level.
            if not self._looks_like_enum_declaration():
                self._skip_to_next_enum()
            return

        if self._parse_enum_body():
            self._expect_declaration_semicolon()

    def _parse_enum_body(self) -> bool:
        # EnumBody := CaseDecl+
        saw_item = False
        last_item_had_error = False

        while not self._at_end():
            if self._check(RBRACE):
                if not saw_item:
                    self._add_error(
                        "ключевое слово case", prefer_eof_on_newline=False
                    )
                self._advance()
                return True

            if self._looks_like_enum_declaration():
                if not last_item_had_error:
                    expected = "}" if saw_item else "ключевое слово case"
                    self._add_error(expected, prefer_eof_on_newline=False)
                return False

            saw_item = True
            if self._check(CASE):
                last_item_had_error = not self._parse_case_declaration()
            else:
                last_item_had_error = True
                self._parse_bad_case_declaration()

        if not last_item_had_error:
            expected = "}" if saw_item else "ключевое слово case"
            self._add_error(expected)
        return False

    def _parse_case_declaration(self) -> bool:
        # CaseDecl := case Identifier ;
        self._advance()

        if not self._consume(IDENTIFIER):
            self._add_error("идентификатор")
            self._recover_after_missing_case_identifier()
            return False

        if not self._consume(SEMICOLON):
            self._add_error(";")
            self._skip_to_case_boundary(consume_semicolon=True)
            return False

        return True

    def _parse_bad_case_declaration(self) -> None:
        # A malformed case item, for example "ccas monday;".
        self._add_error("ключевое слово case", prefer_eof_on_newline=False)

        if self._check(SEMICOLON):
            self._advance()
            return

        if not self._at_end():
            self._advance()

        self._skip_to_case_boundary(consume_semicolon=True)

    def _prepare_tokens(self, scanner_tokens: List[list]) -> None:
        for token in scanner_tokens:
            code, _, lexeme, position = token
            if code == SPACE or code == "ERROR":
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

    def _check(self, *codes: int) -> bool:
        current = self._current()
        return current is not None and current.code in codes

    def _peek_code(self, offset: int) -> Optional[int]:
        index = self.pos + offset
        if index >= len(self.tokens):
            return None
        return self.tokens[index].code

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

    def _expect(
        self, code: int, expected: str, prefer_eof_on_newline: bool = True
    ) -> bool:
        if self._consume(code):
            return True

        self._add_error(expected, prefer_eof_on_newline=prefer_eof_on_newline)
        return False

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

    def _starts_enum_body(self) -> bool:
        return self._check(CASE, IDENTIFIER)

    def _looks_like_enum_declaration(self) -> bool:
        return (
            self._check(ENUM)
            and self._peek_code(1) == IDENTIFIER
            and self._peek_code(2) == LBRACE
        )

    def _recover_after_missing_case_identifier(self) -> None:
        if self._check(SEMICOLON):
            self._advance()
            return

        # Recovery for "case enum;" or "case case;" where a keyword is used
        # instead of an identifier.
        if self._check(ENUM, CASE) and self._peek_code(1) == SEMICOLON:
            self._advance()
            self._advance()
            return

        if self._check(ENUM) and not self._looks_like_enum_declaration():
            self._advance()

        self._skip_to_case_boundary(consume_semicolon=True)

    def _skip_to_case_boundary(self, consume_semicolon: bool) -> None:
        while not self._at_end():
            if self._check(CASE, RBRACE):
                return

            if self._looks_like_enum_declaration():
                return

            if self._check(SEMICOLON):
                if consume_semicolon:
                    self._advance()
                return

            self._advance()

    def _expect_declaration_semicolon(self) -> None:
        if self._consume(SEMICOLON):
            return

        self._add_error(";")

        # If the next enum has already started, leave it for Program.
        if self._check(ENUM) or self._at_end():
            return

        self._skip_to_next_enum()

    def _skip_to_next_enum(self) -> None:
        while not self._at_end() and not self._check(ENUM):
            self._advance()
