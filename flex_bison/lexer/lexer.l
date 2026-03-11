%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int line_num = 1;
int column_num = 1;

// Коды из твоего cods.py
#define CODE_ENUM 1
#define CODE_CASE 2
#define CODE_STRING_TYPE 3
#define CODE_INT_TYPE 4
#define CODE_FLOAT_TYPE 5
#define CODE_DOUBLE_TYPE 6
#define CODE_CHARACTER_TYPE 7
#define CODE_IDENTIFIER 8
#define CODE_COMMA 9
#define CODE_SEMICOLON 10
#define CODE_BRACE_OPEN 11
#define CODE_BRACE_CLOSE 12
#define CODE_SPACE 13
#define CODE_EQUAL 14
#define CODE_COLON 15
#define CODE_STRING 16
#define CODE_INT_DIGIT 17
#define CODE_FLOAT_DIGIT 18

// Функция для вывода токена в формате: код|тип|лексема|позиция
void print_token(int code, const char* type, const char* value, int line, int start, int end) {
    printf("%d|%s|%s|строка %d, %d-%d\n", 
           code, type, value, line, start, end);
}
%}

%option noyywrap
%option yylineno

%%

\n                      { line_num++; column_num = 1; }

[ \t]+                  { 
    print_token(CODE_SPACE, "space", " ", line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

"enum"                  { 
    print_token(CODE_ENUM, "enum", yytext, line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

"case"                  { 
    print_token(CODE_CASE, "case", yytext, line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

"String"                { 
    print_token(CODE_STRING_TYPE, "String", yytext, line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

"Int"                   { 
    print_token(CODE_INT_TYPE, "Int", yytext, line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

"Float"                 { 
    print_token(CODE_FLOAT_TYPE, "Float", yytext, line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

"Double"                { 
    print_token(CODE_DOUBLE_TYPE, "Double", yytext, line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

"Character"             { 
    print_token(CODE_CHARACTER_TYPE, "Character", yytext, line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

[a-zA-Z_][a-zA-Z0-9_]*  { 
    print_token(CODE_IDENTIFIER, "identifier", yytext, line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

[0-9]+                  { 
    print_token(CODE_INT_DIGIT, "int digit", yytext, line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

[0-9]+\.[0-9]+          { 
    print_token(CODE_FLOAT_DIGIT, "float digit", yytext, line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

\"[^\"]*\"              { 
    print_token(CODE_STRING, "string", yytext, line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

"{"                     { 
    print_token(CODE_BRACE_OPEN, "brace open", yytext, line_num, column_num, column_num);
    column_num++; 
}

"}"                     { 
    print_token(CODE_BRACE_CLOSE, "brace close", yytext, line_num, column_num, column_num);
    column_num++; 
}

"="                     { 
    print_token(CODE_EQUAL, "equal", yytext, line_num, column_num, column_num);
    column_num++; 
}

":"                     { 
    print_token(CODE_COLON, "colon", yytext, line_num, column_num, column_num);
    column_num++; 
}

","                     { 
    print_token(CODE_COMMA, "comma", yytext, line_num, column_num, column_num);
    column_num++; 
}

";"                     { 
    print_token(CODE_SEMICOLON, "semicolon", yytext, line_num, column_num, column_num);
    column_num++; 
}

.                       { 
    printf("ERROR|invalid symbol|%s|строка %d, %d\n", yytext, line_num, column_num);
    column_num++; 
}

%%

int main() {
    yylex();
    return 0;
}