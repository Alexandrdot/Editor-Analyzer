%option noyywrap
%option nounput
%option noinput

%{
#include <stdio.h>
#include <string.h>
#include "parser.tab.h"

extern int yylineno;
extern char *yytext;

void count_lines(void);
%}

%%

enum                { count_lines(); return ENUM; }
case                { count_lines(); return CASE; }
[a-zA-Z_][a-zA-Z0-9_]*  { count_lines(); yylval.str = strdup(yytext); return IDENTIFIER; }
";"                 { count_lines(); return SEMICOLON; }
":"                 { count_lines(); return COLON; }
"{"                 { count_lines(); return LBRACE; }
"}"                 { count_lines(); return RBRACE; }
[ \t]+              { /* игнорируем пробелы */ }
\n                  { yylineno++; }
.                   { 
    fprintf(stderr, "DEBUG: Unexpected character '%s' at line %d\n", yytext, yylineno);
    count_lines(); 
    return ERROR; 
}

%%

void count_lines(void) {
    char *c;
    for (c = yytext; *c != '\0'; c++) {
        if (*c == '\n') {
            yylineno++;
        }
    }
}