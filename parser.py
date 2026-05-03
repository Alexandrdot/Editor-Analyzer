from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from cods import ID, LPAREN, MINUS, NUM, PERCENT, PLUS, RPAREN, SLASH, SPACE, STAR


@dataclass
class Token:
    code: int
    lexeme: str
    line: int
    start: int
    end: int
    raw_position: str


class Parser:
    """Рекурсивный спуск: E→TA, T→FB, F→num|id|(E); тетрады и ПОЛИЗ при успехе."""

    def __init__(self, scanner_tokens: List[list], lang: str = "ru"):
        self.syntax_errors: List[dict] = []
        self.tokens: List[Token] = []
        self.pos = 0
        self.last_consumed: Optional[Token] = None
        self.last_line = 1
        self.lang = lang if lang in ("ru", "en") else "ru"
        self.tetrads: List[Tuple[str, str, str, str]] = []
        self.poliz: Optional[List[str]] = None
        self.poliz_value: Optional[int] = None
        self.poliz_note: str = ""
        self._temp_i = 0
        self._error_dedup: set[tuple[str, str]] = set()
        self._prepare_tokens(scanner_tokens)

    def parse(self) -> List[dict]:
        self.tetrads.clear()
        self._temp_i = 0
        self.poliz = None
        self.poliz_value = None
        self.poliz_note = ""
        self.pos = 0
        self.last_consumed = None
        self.syntax_errors.clear()
        self._error_dedup.clear()

        if not self.tokens:
            self._add_error_key("empty_expression")
            return self.syntax_errors

        value = self._parse_E()
        if value is None:
            if not self.syntax_errors:
                self._add_error_key("missing_operand")
        elif not self._at_end():
            cur = self._current()
            if cur is not None and cur.code == RPAREN:
                self._add_error_key("extra_bracket", token=cur)
            else:
                self._add_error_key("unexpected_token", token=cur)
        else:
            self._build_poliz_if_integers_only()

        if self.syntax_errors:
            self.tetrads.clear()
            self.poliz = None
            self.poliz_value = None
            self.poliz_note = ""

        return self.syntax_errors

    def _msg(self, key: str) -> str:
        ru = {
            "empty_expression": "ожидалось арифметическое выражение",
            "missing_operand": "пропущен операнд",
            "extra_bracket": "лишняя закрывающая скобка",
            "expected_rparen": "ожидалось «)»",
            "unexpected_token": "лишний элемент в выражении",
        }
        en = {
            "empty_expression": "expected an arithmetic expression",
            "missing_operand": "missing operand",
            "extra_bracket": "extra closing parenthesis",
            "expected_rparen": "expected ')'",
            "unexpected_token": "unexpected token in expression",
        }
        return (ru if self.lang == "ru" else en)[key]

    def _add_error_key(self, key: str, token: Optional[Token] = None) -> None:
        fragment, position = self._error_location_for_key(key, token)
        dedup_key = (position, key)
        if dedup_key in self._error_dedup:
            return
        self._error_dedup.add(dedup_key)
        prefix = "Синтаксическая ошибка: " if self.lang == "ru" else "Syntax error: "
        self.syntax_errors.append(
            {
                "fragment": fragment,
                "description": prefix + self._msg(key),
                "position": position,
            }
        )

    def _error_location_for_key(
        self, key: str, token: Optional[Token]
    ) -> tuple[str, str]:
        if token is not None:
            return token.lexeme, token.raw_position
        cur = self._current()
        if cur is not None:
            return cur.lexeme, cur.raw_position
        return self._eof_fragment_and_position()

    def _new_temp(self) -> str:
        self._temp_i += 1
        return f"t{self._temp_i}"

    def _emit(self, op: str, a: str, b: str) -> str:
        t = self._new_temp()
        self.tetrads.append((op, a, b, t))
        return t

    def _parse_E(self) -> Optional[str]:
        lhs = self._parse_T()
        if lhs is None:
            return None
        return self._parse_A(lhs)

    def _parse_A(self, lhs: str) -> Optional[str]:
        while self._check(PLUS, MINUS):
            op_tok = self._advance()
            assert op_tok is not None
            op = op_tok.lexeme
            rhs = self._parse_T()
            if rhs is None:
                self._add_error_key("missing_operand")
                return None
            lhs = self._emit(op, lhs, rhs)
        return lhs

    def _parse_T(self) -> Optional[str]:
        lhs = self._parse_F()
        if lhs is None:
            return None
        return self._parse_B(lhs)

    def _parse_B(self, lhs: str) -> Optional[str]:
        while self._check(STAR, SLASH, PERCENT):
            op_tok = self._advance()
            assert op_tok is not None
            op = op_tok.lexeme
            rhs = self._parse_F()
            if rhs is None:
                self._add_error_key("missing_operand")
                return None
            lhs = self._emit(op, lhs, rhs)
        return lhs

    def _parse_F(self) -> Optional[str]:
        if self._at_end():
            self._add_error_key("missing_operand")
            return None

        if self._check(RPAREN):
            cur = self._current()
            self._add_error_key("missing_operand", token=cur)
            return None

        if self._check(PLUS, MINUS, STAR, SLASH, PERCENT):
            return None

        if self._consume(NUM):
            assert self.last_consumed is not None
            return self.last_consumed.lexeme

        if self._consume(ID):
            assert self.last_consumed is not None
            return self.last_consumed.lexeme

        if self._consume(LPAREN):
            inner = self._parse_E()
            if inner is None:
                return None
            if not self._consume(RPAREN):
                self._add_error_key("expected_rparen")
                return None
            return inner

        return None

    def _build_poliz_if_integers_only(self) -> None:
        expr_tokens = [t for t in self.tokens if t.code != SPACE]
        if any(t.code == ID for t in expr_tokens):
            if self.lang == "ru":
                self.poliz_note = (
                    "ПОЛИЗ и числовое значение строятся только для выражений "
                    "из целых литералов (без идентификаторов)."
                )
            else:
                self.poliz_note = (
                    "POLIZ and numeric value are only built for expressions "
                    "with integer literals only (no identifiers)."
                )
            return

        try:
            self.poliz = self._shunting_yard(expr_tokens)
        except ValueError:
            if self.lang == "ru":
                self.poliz_note = "Не удалось построить ПОЛИЗ."
            else:
                self.poliz_note = "Failed to build POLIZ."
            return

        try:
            self.poliz_value = self._eval_rpn(self.poliz)
        except ZeroDivisionError:
            self.poliz_value = None
            if self.lang == "ru":
                self.poliz_note = "Деление на ноль при вычислении ПОЛИЗ."
            else:
                self.poliz_note = "Division by zero when evaluating POLIZ."

    def _shunting_yard(self, expr_tokens: List[Token]) -> List[str]:
        """Алгоритм Дейкстры (сортировочная станция)."""
        out: List[str] = []
        stack: List[str] = []
        prec = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2}

        for t in expr_tokens:
            if t.code == NUM:
                out.append(t.lexeme)
            elif t.code in (PLUS, MINUS, STAR, SLASH, PERCENT):
                op = t.lexeme
                while (
                    stack
                    and stack[-1] != "("
                    and prec.get(stack[-1], 0) >= prec[op]
                ):
                    out.append(stack.pop())
                stack.append(op)
            elif t.code == LPAREN:
                stack.append("(")
            elif t.code == RPAREN:
                while stack and stack[-1] != "(":
                    out.append(stack.pop())
                if not stack or stack[-1] != "(":
                    raise ValueError("mismatched paren")
                stack.pop()
            else:
                raise ValueError("unexpected in poliz")

        while stack:
            if stack[-1] == "(":
                raise ValueError("mismatched paren")
            out.append(stack.pop())
        return out

    def _eval_rpn(self, rpn: List[str]) -> int:
        st: List[int] = []
        ops = {"+", "-", "*", "/", "%"}

        for x in rpn:
            if x in ops:
                b = st.pop()
                a = st.pop()
                if x == "+":
                    st.append(a + b)
                elif x == "-":
                    st.append(a - b)
                elif x == "*":
                    st.append(a * b)
                elif x == "/":
                    st.append(a // b)
                else:
                    st.append(a % b)
            else:
                st.append(int(x, 10))
        return st[0]

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
        if len(nums) >= 2:
            return int(nums[0]), int(nums[1]), int(nums[1])
        raise ValueError(f"Invalid token position: {position}")

    def _current(self) -> Optional[Token]:
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def _at_end(self) -> bool:
        while self._current() is not None and self._current().code == SPACE:
            self.pos += 1
        return self._current() is None

    def _check(self, *codes: int) -> bool:
        self._skip_spaces()
        current = self._current()
        return current is not None and current.code in codes

    def _skip_spaces(self) -> None:
        while self._current() is not None and self._current().code == SPACE:
            self.pos += 1

    def _advance(self) -> Optional[Token]:
        self._skip_spaces()
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

    def _eof_fragment_and_position(self) -> tuple[str, str]:
        if self.last_consumed is not None:
            return (
                "EOF",
                f"строка {self.last_consumed.line}, {self.last_consumed.end}-{self.last_consumed.end}",
            )
        return "EOF", f"строка {self.last_line}, 1-1"
