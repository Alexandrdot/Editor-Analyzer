%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int line_num = 1;
int column_num = 1;

#define CODE_ENUM 1
#define CODE_CASE 2

#define CODE_IDENTIFIER 3

#define CODE_SEMICOLON 4
#define CODE_BRACE_OPEN 5
#define CODE_BRACE_CLOSE 6
#define CODE_SPACE 7


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


[a-zA-Z_][a-zA-Z0-9_]*  { 
    print_token(CODE_IDENTIFIER, "identifier", yytext, line_num, column_num, column_num + yyleng - 1);
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