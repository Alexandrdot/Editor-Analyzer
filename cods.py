CODS_TYPES = {
    1: 'enum', 2: 'case', 3: 'String', 4: 'Int',
    5: 'Float', 6: 'Double', 7: 'Character', 8: 'identifier',
    9: 'comma', 10: 'semicolon', 11: 'brace open', 12: 'brace close',
    13: 'space', 14: 'equal', 15: 'colon', 16: 'string',
    17: 'int digit', 18: 'float digit', 'error': 'invalid symbol'
}

SYMBOLS = {
    ':': 15, ';': 10, ',': 9, '=': 14,
    '{': 11, '}': 12
}

KEYWORDS = {'enum': 1, 'case': 2}

TYPES = {'String': 3, 'Int': 4, 'Float': 5, 'Double': 6, 'Character': 7}
