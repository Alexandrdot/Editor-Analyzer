%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylineno;
extern char *yytext;
extern FILE *yyin;

void yyerror(const char *s);
int yylex(void);

typedef struct {
    char *fragment;
    char *location;
    char *message;
} Error;

Error errors[100];
int error_count = 0;

void add_error(const char *fragment, const char *location, const char *message) {
    if (error_count < 100) {
        errors[error_count].fragment = strdup(fragment);
        errors[error_count].location = strdup(location);
        errors[error_count].message = strdup(message);
        error_count++;
    }
}

void print_errors(void) {
    for (int i = 0; i < error_count; i++) {
        printf("ERROR|%s|%s|%s\n", 
               errors[i].fragment, 
               errors[i].location, 
               errors[i].message);
    }
}

void cleanup_errors(void) {
    for (int i = 0; i < error_count; i++) {
        free(errors[i].fragment);
        free(errors[i].location);
        free(errors[i].message);
    }
    error_count = 0;
}

%}

%union {
    char *str;
}

%token ENUM CASE
%token SEMICOLON COLON LBRACE RBRACE
%token <str> IDENTIFIER
%token ERROR

%start enum_declaration

%%

enum_declaration:
    ENUM IDENTIFIER LBRACE enum_cases RBRACE
    {
        printf("SUCCESS|Enum parsed successfully\n");
    }
    | ENUM error LBRACE enum_cases RBRACE
    {
        add_error(yytext, "line 1, position 1", "Invalid enum name");
        YYABORT;
    }
    | ENUM IDENTIFIER error enum_cases RBRACE
    {
        add_error(yytext, "line 1, position 1", "Missing '{' after enum name");
        YYABORT;
    }
    | ENUM IDENTIFIER LBRACE error RBRACE
    {
        add_error(yytext, "line 1, position 1", "Invalid enum cases structure");
        YYABORT;
    }
    ;

enum_cases:
    enum_case
    | enum_cases enum_case
    ;

enum_case:
    CASE IDENTIFIER SEMICOLON
    | CASE IDENTIFIER COLON error
    {
        char location[50];
        sprintf(location, "line %d, position 1", yylineno);
        add_error(yytext, location, "Expected ';' after case identifier");
        YYABORT;
    }
    | CASE error SEMICOLON
    {
        char location[50];
        sprintf(location, "line %d, position 1", yylineno);
        add_error(yytext, location, "Invalid case identifier");
        YYABORT;
    }
    | error IDENTIFIER SEMICOLON
    {
        char location[50];
        sprintf(location, "line %d, position 1", yylineno);
        add_error(yytext, location, "Expected 'case' keyword");
        YYABORT;
    }
    ;

%%

void yyerror(const char *s) {
    char location[50];
    sprintf(location, "line %d, position 1", yylineno);
    
    if (strstr(s, "syntax error") != NULL) {
        if (strcmp(yytext, "case") == 0) {
            add_error(yytext, location, "Invalid case syntax");
        } else if (strcmp(yytext, "}") == 0) {
            add_error(yytext, location, "Unexpected closing brace");
        } else {
            add_error(yytext, location, s);
        }
    } else {
        add_error(yytext, location, s);
    }
}

int main(int argc, char **argv) {
    if (argc > 1) {
        FILE *file = fopen(argv[1], "r");
        if (!file) {
            fprintf(stderr, "DEBUG: Could not open file %s\n", argv[1]);
            return 1;
        }
        yyin = file;
    }
    
    yylineno = 1;
    error_count = 0;
    
    int result = yyparse();
    
    if (result == 0 && error_count == 0) {
        printf("SUCCESS|Parsing completed successfully\n");
    } else {
        print_errors();
    }
    
    cleanup_errors();
    
    if (argc > 1) {
        fclose(yyin);
    }
    
    return (result == 0 && error_count == 0) ? 0 : 1;
}