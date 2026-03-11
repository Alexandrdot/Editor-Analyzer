%{
#include "parser.tab.h"
#include <string.h>

int line_num = 1;
%}

%option noyywrap
%option yylineno

%%

[ \t]+          { /* игнорируем */ }
\n              { line_num++; }

"enum"          { return ENUM; }
"case"          { return CASE; }

"String"        { yylval.string = strdup(yytext); return TYPE; }
"Int"           { yylval.string = strdup(yytext); return TYPE; }
"Float"         { yylval.string = strdup(yytext); return TYPE; }
"Double"        { yylval.string = strdup(yytext); return TYPE; }
"Character"     { yylval.string = strdup(yytext); return TYPE; }

[a-zA-Z_][a-zA-Z0-9_]* { 
    yylval.string = strdup(yytext); 
    return IDENTIFIER; 
}

[0-9]+          { 
    yylval.int_val = atoi(yytext); 
    return INTEGER; 
}

[0-9]+\.[0-9]+  { 
    yylval.float_val = atof(yytext); 
    return FLOAT; 
}

\"[^\"]*\"      { 
    yytext[yyleng-1] = '\0';
    yylval.string = strdup(yytext+1);
    return STRING; 
}

"{"             { return LBRACE; }
"}"             { return RBRACE; }
"="             { return ASSIGN; }
":"             { return COLON; }
","             { return COMMA; }
";"             { return SEMICOLON; }

.               { /* игнорируем */ }

%%