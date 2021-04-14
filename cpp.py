import sys
from ply.lex import LexToken
import ply.yacc as yacc


class Table:
    def __init__(self, name=""):
        self.variables = {}
        self.name = name

    @staticmethod
    def line(length=20):
        print("-" * length)

    def insert(self, var, var_type):
        # print("Inserting.......",var_type)
        if var in self.variables.keys():
            print(var, "has already been declared")
        else:
            self.variables[var] = {
                "name": var,
                "type": "Default_type",
                "value": 0,
                "address": -1,
                "code": 1,
            }  # 1->recently added, 0 otherwise
            self.variables[var]["address"] = hex(id(self.variables[var]["name"]))

    def display(self):
        if len(self.variables) == 0:
            print("Empty table")
            return

        self.line(60)
        print(f"\t\tTable for : {self.name} scope")
        self.line(60)
        print("\tID\tTYPE\tVALUE\tADDRESS")

        for key in self.variables.keys():
            print("\t", end="")
            print(self.variables[key]["name"], end="\t")
            print(self.variables[key]["type"], end="\t")
            print(self.variables[key]["value"], end="\t")
            print(self.variables[key]["address"])
        print()

    def update_type(self, new_type):
        for key in self.variables.keys():
            if self.variables[key]["code"]:
                self.variables[key]["type"] = new_type
                self.variables[key]["code"] = 0

                if new_type == "INT":
                    self.variables[key]["value"] = 0
                elif new_type == "CHAR":
                    self.variables[key]["value"] = ""
                elif new_type == "FLOAT":
                    self.variables[key]["value"] = 0.0

    def update_val(self, var, new_val):
        try:
            self.variables[var]["value"] = self.variables[new_val]["value"]
        except:
            if var not in self.variables.keys():
                print(var, "not declared")
            else:
                self.variables[var]["value"] = new_val


tables = []
stack = [Table("GLOBAL")]

reserved = (
    "AUTO",
    "BREAK",
    "CASE",
    "CHAR",
    "CONST",
    "CONTINUE",
    "DEFAULT",
    "DO",
    "DOUBLE",
    "ELSE",
    "ENUM",
    "EXTERN",
    "FLOAT",
    "FOR",
    "GOTO",
    "IF",
    "INT",
    "LONG",
    "REGISTER",
    "RETURN",
    "SHORT",
    "SIGNED",
    "SIZEOF",
    "STATIC",
    "STRUCT",
    "SWITCH",
    "TYPEDEF",
    "UNION",
    "UNSIGNED",
    "VOID",
    "VOLATILE",
    "WHILE",
    "PRINTF",
)

tokens = reserved + (
    # Literals (identifier, integer constant, float constant, string constant,
    # char const)
    "ID",
    "TYPEID",
    "ICONST",
    "FCONST",
    "SCONST",
    "CCONST",
    # Operators (+,-,*,/,%,|,&,~,^,<<,>>, ||, &&, !, <, <=, >, >=, ==, !=)
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "MOD",
    "OR",
    "AND",
    "NOT",
    "XOR",
    "LSHIFT",
    "RSHIFT",
    "LOR",
    "LAND",
    "LNOT",
    "LT",
    "LE",
    "GT",
    "GE",
    "EQ",
    "NE",
    # Assignment (=, *=, /=, %=, +=, -=, <<=, >>=, &=, ^=, |=)
    "EQUALS",
    "TIMESEQUAL",
    "DIVEQUAL",
    "MODEQUAL",
    "PLUSEQUAL",
    "MINUSEQUAL",
    "LSHIFTEQUAL",
    "RSHIFTEQUAL",
    "ANDEQUAL",
    "XOREQUAL",
    "OREQUAL",
    # Increment/decrement (++,--)
    "PLUSPLUS",
    "MINUSMINUS",
    # Structure dereference (->)
    "ARROW",
    # Conditional operator (?)
    "CONDOP",
    # Delimeters ( ) [ ] { } , . ; :
    "LPAREN",
    "RPAREN",
    "LBRACKET",
    "RBRACKET",
    "LBRACE",
    "RBRACE",
    "COMMA",
    "PERIOD",
    "SEMI",
    "COLON",
    # Ellipsis (...)
    "ELLIPSIS",
)


def p_start(p):
    """
    start : statement
    """
    p[0] = p[1]


def p_while(p):
    """
    while :  WHILE LPAREN cond RPAREN LBRACE new_scope statement RBRACE
    """
    p[0] = ("while", p[3], p[5], p[7], p[8])

    print("Deleting scope table")
    tables.append(stack.pop())
    tables[-1].name = "WHILE"


def p_if(p):
    """
    if : IF LPAREN cond RPAREN LBRACE new_scope statement RBRACE optional
    """
    p[0] = ("if", p[3], p[5], p[7], p[8])

    print("Deleting scope table")
    tables.append(stack.pop())
    tables[-1].name = "IF"


def p_optional_1(p):
    """
    optional : empty
    """
    p[0] = p[1]


def p_optional(p):
    """
    optional : ELSE LBRACE new_scope statement RBRACE
    """
    p[0] = ("else", p[2], p[4], p[5])

    print("Deleting scope table")
    tables.append(stack.pop())
    tables[-1].name = "ELSE"


def p_switch(p):
    """
    switch : SWITCH LPAREN switch_expr RPAREN LBRACE labeled_statement RBRACE
    """
    # exp should be defined
    p[0] = ("switch", p[3], p[5], p[6], p[7])


def p_switch_expr(p):
    """
    switch_expr : cond
        | expr
        | const_expr
        | assign
        | ID
    """
    p[0] = p[1]


def p_labeled_statement(p):
    """
    labeled_statement : CASE const_expr COLON statement
    """
    p[0] = ("case", p[2], p[4])


def p_labeled_statement_1(p):
    """
    labeled_statement :  DEFAULT COLON statement
    """
    p[0] = ("default", p[3])


def p_labeled_statement_2(p):
    """
    labeled_statement :  labeled_statement labeled_statement
    """
    p[0] = ("labeled_statement", p[1], p[2])


def p_labeled_statement_3(p):
    """
    labeled_statement :  labeled_statement BREAK SEMI labeled_statement
    """
    p[0] = ("labeled_statement", p[1], p[3])


def p_labeled_statement_4(p):
    """
    labeled_statement : empty
    """
    p[0] = p[1]


def p_const_expr(p):
    """
    const_expr : ICONST
                | CCONST
    """
    p[0] = p[1]


#
# def p_print(p):
#     '''
#     print : COUT LSHIFT out_statements SEMI
#     '''
#     p[0] = ('cout',p[3])


def p_out_statements(p):
    """
    out_statements : possibilities
    """
    p[0] = p[1]


def p_out_statements_1(p):
    """
    out_statements : possibilities LSHIFT out_statements
    """
    p[0] = (p[1], "outstream_operator", p[3])


def p_possibilities(p):
    """
    possibilities : ID
                | ICONST
                | CCONST
                | FCONST
                | SCONST
    """
    p[0] = p[1]


# def p_statement_list(p):
#     '''
#     statement_list : statement statement_list
#     '''
#     p[0] = (p[1], p[2])


def p_statement_3(p):
    """
    statement : statement SEMI statement
    """
    p[0] = (p[1], "NEXT LINE", p[3])


def p_statement_4(p):
    """
    statement : statement SEMI
    """
    p[0] = p[1]


def p_statement_5(p):
    """
    statement : unary
                | assign
                | declaration
                | while
                | for
                | if
                | switch
    """
    p[0] = p[1]


def p_for(p):
    """
    for :  FOR LPAREN assign SEMI cond SEMI unary RPAREN LBRACE new_scope statement RBRACE
    """
    p[0] = ("for", p[3], p[5], p[7], p[9], p[10], p[11])

    print("Deleting scope table")
    tables.append(stack.pop())
    tables[-1].name = "FOR"


def p_new_scope(p):
    """
    new_scope :
    """
    stack.append(Table())
    print("Created a new scope table")


def p_statement(p):
    """
    statement : empty
    """


def p_empty(p):
    "empty :"
    pass


def p_assign_exp(p):
    """
    assign : ID EQUALS expr
    """
    p[0] = ("EXPRESSION CALCULATED", "=", p[1], p[3])
    stack[-1].update_val(p[1], p[3])


def p_assign_expid(p):
    """
    assign : ID EQUALS exprid
    """
    p[0] = ("=", p[1], p[3])
    stack[-1].update_val(p[1], p[3])


def p_assign(p):
    """
    assign : ID EQUALS ICONST
       | ID EQUALS FCONST
       | ID EQUALS CCONST
       | ID EQUALS ID
    """
    p[0] = ("ASSIGN", "=", p[1], p[3])
    stack[-1].update_val(p[1], p[3])


def p_cond(p):
    """
    cond : ID LT ICONST
        | ID LE ICONST
        | ID GE ICONST
        | ID GT ICONST
        | ID LT ID
        | ID LE ID
        | ID GE ID
        | ID GT ID
        | ID NE ICONST
        | ID NE ID
        | ID NE FCONST
        | ICONST NE ID
        | ICONST NE ICONST
        | ID LE FCONST
        | ID GE FCONST
        | ID GT FCONST
        | ID LT FCONST
        | ICONST LE ICONST
        | ICONST GE ICONST
        | ICONST GT ICONST
        | ICONST LT ICONST
        | FCONST LE FCONST
        | FCONST GE FCONST
        | FCONST GT FCONST
        | FCONST LT FCONST
        | ID EQ ID
        | ID EQ ICONST
        | ID EQ FCONST
        | ICONST EQ ID
        | FCONST EQ ID
        | ICONST EQ ICONST
        | FCONST EQ FCONST
    """
    if p[2] == "LE":
        p[0] = ("CONDI", "<=", p[1], p[3])
    elif p[2] == "LT":
        p[0] = ("CONDI", "<", p[1], p[3])
    elif p[2] == "GE":
        p[0] = ("CONDI", ">=", p[1], p[3])
    elif p[2] == "GT":
        p[0] = ("CONDI", ">", p[1], p[3])
    elif p[2] == "EQ":
        p[0] = ("CONDI", "==", p[1], p[3])
    elif p[2] == "NE":
        p[0] = ("CONDI", "!=", p[1], p[3])


def p_cond_1(p):
    """
    cond : ID
    """
    p[0] = p[1]


def p_unary_pre(p):
    """
    unary : PLUSPLUS ID
       | MINUSMINUS ID
    """
    if p[1] == "PLUSPLUS":
        p[0] = ("PREINC", "++", p[2])
    elif p[1] == "MINUSMINUS":
        p[0] = ("PREDEC", "--", p[2])


def p_unary_post(p):
    """
    unary : ID PLUSPLUS
       | ID MINUSMINUS
    """
    if p[2] == "PLUSPLUS":
        p[0] = ("POSTINC", "++", p[1])
    elif p[2] == "MINUSMINUS":
        p[0] = ("POSTDEC", "--", p[1])


def p_declaration(p):
    """
    declaration : types vee
    """
    p[0] = (p[2], p[1])
    # Update the types of the above declared variables
    stack[-1].update_type(p[1])


def p_types(p):
    """
    types : INT
        | FLOAT
        | DOUBLE
        | CHAR
        | LONG
        | REGISTER
    """
    p[0] = p[1]


def p_vee(p):
    """
    vee : vee COMMA ID
    """
    p[0] = (p[1], ",", p[3])
    stack[-1].insert(p[3], "")


def p_vee_1(p):
    """
    vee : ID
    """
    p[0] = p[1]
    stack[-1].insert(p[1], "")


def p_expr(p):
    """
    expr : expr PLUS term
    expr : expr MINUS term
    """
    if p[2] == "PLUS" and ((p[3])[1] == "INT" and (p[1])[1] == "INT"):
        p[0] = int((p[1])[0]) + int((p[3])[0])
    elif p[2] == "PLUS" and ((p[3])[1] == "FLOAT" or (p[1])[1] == "FLOAT"):
        p[0] = float((p[1])[0]) + float((p[3])[0])
    elif p[2] == "MINUS" and ((p[3])[1] == "INT" and (p[1])[1] == "INT"):
        p[0] = int((p[1])[0]) - int((p[3])[0])
    elif p[2] == "MINUS" and ((p[3])[1] == "FLOAT" or (p[1])[1] == "FLOAT"):
        p[0] = float((p[1])[0]) - float((p[3])[0])
    # print('UPDATE SYMBOL TABLE','(',p[0],',','FLOAT,',p.lineno)


def p_expr_1(p):
    """
    expr : term
    """
    p[0] = p[1]


def p_exprid(p):
    """
    exprid : exprid PLUS termid
    exprid : exprid MINUS termid
    """
    if p[2] == "PLUS":
        p[0] = ("+", p[1], p[3])
    if p[2] == "MINUS":
        p[0] = ("-", p[1], p[3])


def p_exprid_1(p):
    """
    exprid : termid
    """
    p[0] = p[1]


# def expr_1(p):
#    '''
#   expr : expr MINUS term
#  '''
# p[0]=(p[1],'-',p[3])
def p_term(p):
    """
    term : term TIMES factor
    term : term DIVIDE factor
    """
    if p[2] == "TIMES" and ((p[3])[1] == "INT" and (p[1])[1] == "INT"):
        p[0] = ((int((p[1])[0]) * int((p[3])[0])), "INT")
    elif p[2] == "TIMES" and ((p[3])[1] == "FLOAT" or (p[1])[1] == "FLOAT"):
        p[0] = ((float((p[1])[0]) * float((p[3])[0])), "FLOAT")
    # print("HELLO")
    # print("UPDATE SYMBOL TABLE","(",p[2],",","FLOAT,",p.lineno)
    elif p[2] == "DIVIDE" and ((p[3])[1] == "INT" and (p[1])[1] == "INT"):
        p[0] = ((int((p[1])[0]) / int((p[3])[0])), "INT")
    elif p[2] == "DIVIDE" and ((p[3])[1] == "FLOAT" or (p[1])[1] == "FLOAT"):
        p[0] = ((float((p[1])[0]) / float((p[3])[0])), "FLOAT")
    # print('UPDATE SYMBOL TABLE','(',p[0],',','FLOAT,',p.lineno)


def p_termid(p):
    """
    termid : termid TIMES factorid
    termid : termid DIVIDE factorid
    """
    if p[2] == "TIMES":
        p[0] = ("*", p[1], p[3])
    elif p[2] == "DIVIDE":
        p[0] = ("/", p[1], p[3])


def p_term_1(p):
    """
    term : factor
    """
    p[0] = p[1]


def p_termid_1(p):
    """
    termid : factorid
    """
    p[0] = p[1]


def p_factor(p):
    """
    factor : ICONST
    """
    p[0] = (p[1], "INT")


def p_factor_8(p):
    """
    factor : FCONST
    """
    p[0] = (p[1], "FLOAT")


def p_factorid(p):
    """
    factorid : ID
    """
    p[0] = p[1]


def p_error(p):
    if p:
        print("Syntax error in input!\t Line no:", p.lineno)


def display_all_tables():
    tables.append(stack.pop())
    while len(tables) > 0:
        t = tables.pop()
        t.display()


def get_token_line():
    global tokens_lines
    result = tokens_lines[0].strip()
    tokens_lines = tokens_lines[1:]
    return result


pa2_tokens = []


class PA2Lexer(object):
    def token(whatever):
        global pa2_tokens
        if pa2_tokens == []:
            return None
        (line, token_type, lexeme) = pa2_tokens[0]
        pa2_tokens = pa2_tokens[1:]
        tok = LexToken()
        tok.type = token_type
        tok.value = lexeme
        tok.lineno = line
        tok.lexpos = 0
        return tok

    # tok.type, tok.value, tok.lineno, tok.lexpos


if __name__ == "__main__":

    tokens_filename = sys.argv[1]
    tokens_filehandle = open(tokens_filename, "r")
    tokens_lines = tokens_filehandle.readlines()
    tokens_filehandle.close()

    while tokens_lines != []:
        line_number = get_token_line()
        token_type = get_token_line()
        token_lexeme = token_type
        if token_type in ["ID", "TYPEID", "ICONST", "FCONST", "SCONST", "CCONST"]:
            token_lexeme = get_token_line()
        pa2_tokens = pa2_tokens + [(line_number, token_type.upper(), token_lexeme)]
    # print(pa2_tokens)

    pa2lexer = PA2Lexer()

    parser = yacc.yacc()
    ast = yacc.parse(lexer=pa2lexer)
    print(ast)

    display_all_tables()
    print("Done!")