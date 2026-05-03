NUM = 1
ID = 2
PLUS = 3
MINUS = 4
STAR = 5
SLASH = 6
PERCENT = 7
LPAREN = 8
RPAREN = 9
SPACE = 10

CODS_TYPES = {
    NUM: "number",
    ID: "identifier",
    PLUS: "plus",
    MINUS: "minus",
    STAR: "multiply",
    SLASH: "divide",
    PERCENT: "modulo",
    LPAREN: "paren open",
    RPAREN: "paren close",
    SPACE: "space",
    "error": "invalid symbol",
}

SYMBOLS = {
    "+": PLUS,
    "-": MINUS,
    "*": STAR,
    "/": SLASH,
    "%": PERCENT,
    "(": LPAREN,
    ")": RPAREN,
}

KEYWORDS: dict[str, int] = {}
