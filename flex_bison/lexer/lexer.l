%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int line_num = 1;
int column_num = 1;
int start_error_col = 0;
char error_buffer[1024];

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

// Функция для вывода сгруппированной ошибки
void print_error(const char* value, int line, int start, int end) {
    printf("ERROR|invalid symbol|%s|строка %d, %d-%d\n", 
           value, line, start, end);
}

// Флаг для отслеживания накопления ошибок
int in_error_state = 0;
%}

%option noyywrap
%option yylineno

%%

\n                      { 
    if (in_error_state) {
        // Если были накоплены ошибки, выводим их одной группой
        print_error(error_buffer, line_num, start_error_col, column_num - 1);
        in_error_state = 0;
        error_buffer[0] = '\0';
    }
    line_num++; 
    column_num = 1; 
}

[ \t]+                  { 
    if (in_error_state) {
        // Если были накоплены ошибки, выводим их одной группой
        print_error(error_buffer, line_num, start_error_col, column_num - 1);
        in_error_state = 0;
        error_buffer[0] = '\0';
    }
    print_token(CODE_SPACE, "space", " ", line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

"enum"                  { 
    if (in_error_state) {
        print_error(error_buffer, line_num, start_error_col, column_num - 1);
        in_error_state = 0;
        error_buffer[0] = '\0';
    }
    print_token(CODE_ENUM, "enum", yytext, line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

"case"                  { 
    if (in_error_state) {
        print_error(error_buffer, line_num, start_error_col, column_num - 1);
        in_error_state = 0;
        error_buffer[0] = '\0';
    }
    print_token(CODE_CASE, "case", yytext, line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

[a-zA-Z_][a-zA-Z0-9_]*  { 
    if (in_error_state) {
        print_error(error_buffer, line_num, start_error_col, column_num - 1);
        in_error_state = 0;
        error_buffer[0] = '\0';
    }
    print_token(CODE_IDENTIFIER, "identifier", yytext, line_num, column_num, column_num + yyleng - 1);
    column_num += yyleng; 
}

"{"                     { 
    if (in_error_state) {
        print_error(error_buffer, line_num, start_error_col, column_num - 1);
        in_error_state = 0;
        error_buffer[0] = '\0';
    }
    print_token(CODE_BRACE_OPEN, "brace open", yytext, line_num, column_num, column_num);
    column_num++; 
}

"}"                     { 
    if (in_error_state) {
        print_error(error_buffer, line_num, start_error_col, column_num - 1);
        in_error_state = 0;
        error_buffer[0] = '\0';
    }
    print_token(CODE_BRACE_CLOSE, "brace close", yytext, line_num, column_num, column_num);
    column_num++; 
}

";"                     { 
    if (in_error_state) {
        print_error(error_buffer, line_num, start_error_col, column_num - 1);
        in_error_state = 0;
        error_buffer[0] = '\0';
    }
    print_token(CODE_SEMICOLON, "semicolon", yytext, line_num, column_num, column_num);
    column_num++; 
}

.                       { 
    // Если это первый недопустимый символ, запоминаем начальную позицию
    if (!in_error_state) {
        in_error_state = 1;
        start_error_col = column_num;
        error_buffer[0] = '\0';
    }
    
    // Добавляем символ в буфер ошибки
    strncat(error_buffer, yytext, sizeof(error_buffer) - strlen(error_buffer) - 1);
    column_num += yyleng; 
}

%%

int main() {
    yylex();
    
    // Если файл закончился, а ошибка осталась - выводим
    if (in_error_state) {
        print_error(error_buffer, line_num, start_error_col, column_num - 1);
    }
    
    return 0;
}