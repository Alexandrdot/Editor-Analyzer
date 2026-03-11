%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylex();
extern int yyparse();
extern FILE* yyin;
extern int line_num;

void yyerror(const char *s);
int syntax_error = 0;
%}

%union {
    int int_val;
    float float_val;
    char* string;
}

%token ENUM CASE TYPE IDENTIFIER
%token INTEGER FLOAT STRING
%token LBRACE RBRACE ASSIGN COLON COMMA SEMICOLON SPACE

%type <string> ENUM CASE TYPE IDENTIFIER STRING
%type <int_val> INTEGER
%type <float_val> FLOAT

%start program

%%

program:
    /* пусто */
    | program enum_decl
    | program error
    ;

enum_decl:
    ENUM IDENTIFIER LBRACE case_list RBRACE
    | ENUM IDENTIFIER COLON TYPE LBRACE case_list RBRACE
    ;

case_list:
    case_item
    | case_list COMMA case_item
    | case_list case_item
    ;

case_item:
    CASE IDENTIFIER
    | CASE IDENTIFIER ASSIGN literal
    | IDENTIFIER
    | IDENTIFIER ASSIGN literal
    ;

literal:
    INTEGER
    | FLOAT
    | STRING
    ;

%%

void yyerror(const char *s) {
    fprintf(stderr, "Ошибка в строке %d: %s\n", line_num, s);
    syntax_error = 1;
}

int main(int argc, char** argv) {
    if (argc > 1) {
        FILE* file = fopen(argv[1], "r");
        if (!file) {
            fprintf(stderr, "Не могу открыть файл %s\n", argv[1]);
            return 1;
        }
        yyin = file;
    }
    
    syntax_error = 0;
    int result = yyparse();
    
    if (result == 0 && syntax_error == 0) {
        printf("✅ Синтаксис корректный!\n");
        return 0;
    } else {
        printf("❌ Синтаксические ошибки!\n");
        return 1;
    }
}