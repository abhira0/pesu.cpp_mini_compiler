import argparse
import pickle
import sys

import ply.lex as lex
import ply.yacc as yacc
from ply.lex import LexToken

from tokrules import *

cached_input = """
int              a;
/*
fgrhjfbkjnij
djvhgdhjbfdhb \n \n 563e

*/
int b;
int a;
a = 40;
for( b = 50; c<10; c++) {
switch (a){
case 4: int y; int po;break;
default: float sfas;
// haha
}
}
"""

"""-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_"""


class ClassSymbolTable:
    def __init__(self):
        self.symbols = dict()

    @staticmethod
    def line(length=20):
        print("-" * length)

    def insert(self, var):
        if var in self.symbols.keys():
            # print(var,"Sym Tab: has already been declared")
            pass
        else:
            # print("Inserting.......",var)
            self.symbols[var] = {"name": var, "type": None, "value": None}

    def display(self):
        if len(self.symbols) == 0:
            print("Empty table")
            return

        self.line(60)
        print("\tID\tTYPE\t\tVALUE\t")

        for key in self.symbols.keys():
            print("\t", end="")
            print(self.symbols[key]["name"], end="\t")
            print(self.symbols[key]["type"], end="\t\t")
            print(self.symbols[key]["value"])
        print()

    def update_val(self, var, new_val):
        self.symbols[var]["value"] = new_val

    def update_type(self, var, var_type):
        if var_type == type(str()):
            t = "CHAR"
        elif var_type == type(int()):
            t = "INT"
        elif var_type == type(float()):
            t = "FLOAT"
        self.symbols[var]["type"] = t


class Table:
    def __init__(self, name=""):
        self.variables = {}
        self.name = name
        self.types = {"INT": type(int()), "FLOAT": type(float()), "CHAR": type(str())}

    @staticmethod
    def line(length=20):
        print("-" * length)

    def insert(self, var, var_type):
        # print("Inserting.......",var_type)
        if var in self.variables.keys():
            print(var, "has already been declared in Line no.", id_map[var]["line_no"])
            raise ValueError
        else:
            self.variables[var] = {
                "name": var,
                "type": "Default_type",
                "value": None,
                "address": -1,
                "lineno": id_map[var]["line_no"],
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
        print("\tID\tTYPE\tVALUE\tADDRESS\t\tLINE_NO")

        for key in self.variables.keys():
            print("\t", end="")
            print(self.variables[key]["name"], end="\t")
            print(self.variables[key]["type"], end="\t")
            print(self.variables[key]["value"], end="\t")
            print(self.variables[key]["address"], end="\t")
            print(self.variables[key]["lineno"])
        print()

    def update_type(self, new_type):
        for key in self.variables.keys():
            if self.variables[key]["code"]:
                self.variables[key]["type"] = new_type

                if self.variables[key]["value"] != None and self.types[
                    new_type
                ] != type(self.variables[key]["value"]):
                    print(
                        f'Type of {key} does not match {self.variables[key]["value"]}!'
                    )

                self.variables[key]["code"] = 0

                if self.variables[key]["value"] == None:
                    if new_type == "INT":
                        self.variables[key]["value"] = 0
                    elif new_type == "CHAR":
                        self.variables[key]["value"] = ""
                    elif new_type == "FLOAT":
                        self.variables[key]["value"] = 0.0

    def update_val(self, var, new_val):
        try:
            if not isDeclared(var):
                displayNotDeclared(var)
            else:
                if get_val(new_val) == None:
                    raise Exception
                else:
                    set_val(var, get_val(new_val))
        except Exception:
            if not isDeclared(var):
                displayNotDeclared(var)
            else:
                t = get_type(var)  # self.variables[var]['type']
                if t != "Default_type" and self.types[t] != type(new_val):
                    print(f"Type of {var} does not match {new_val}!")
                set_val(var, new_val)


tables = []
stack = [Table("GLOBAL")]
label_stack = ["l"]
label_stack_no = [0]
switch_expr = None
cases_list = []
SymbolTable = ClassSymbolTable()

temp_var_no = 0


def get_type(var):
    i = len(stack) - 1
    while i >= 0:
        if var in stack[i].variables:
            return stack[i].variables[var]["type"]
        i -= 1


def set_val(var, val):
    i = len(stack) - 1
    while i >= 0:
        if var in stack[i].variables:
            stack[i].variables[var]["value"] = val
            break
        i -= 1


def get_val(var):
    i = len(stack) - 1
    while i >= 0:
        if var in stack[i].variables:
            return stack[i].variables[var]["value"]
        i -= 1


def _get_value(x):
    try:
        return int(x)
    except:
        ...

    try:
        return float(x)
    except:
        ...

    return x


def isDeclared(var):
    if var not in id_map:
        return True

    i = len(stack) - 1
    while i >= 0:
        if var in stack[i].variables:
            return True
        i -= 1

    return False


def displayNotDeclared(var):
    # print(f"{var} has not been declared. Line no. {id_map[var]['line_no']}")
    print(f"{var} has not been declared. ")


def print_label():
    global label_stack
    global label_stack_no
    print(f"{label_stack[-1]}{label_stack_no[-1]}:")
    label_stack_no[-1] += 1


def goto(label, _print=True):
    s = f"\tGOTO\t\t\t{label}"
    if _print:
        print(s)
    return s


def assign(dst, rs, _print=True):
    s = ""
    # variable not in id_map => variable is a temp variable
    if rs not in id_map and dst not in id_map:
        s += f"\tASSIGN\t{rs}\t\t{dst}"
        SymbolTable.insert(dst)
    elif rs in id_map and dst not in id_map:
        temp = id_map[rs]["scope"][-1] - 1
        s += f"\tASSIGN\t{rs}_{temp}\t\t{dst}"
        SymbolTable.insert(dst)
    elif rs not in id_map and dst in id_map:
        s += f"\tASSIGN\t{rs}\t\t{dst}_{id_map[dst]['version_no']}"
        SymbolTable.insert(f"{dst}_{id_map[dst]['version_no']}")
        id_map[dst]["version_no"] += 1
        id_map[dst]["scope"][-1] = id_map[dst]["version_no"]
    else:
        temp = id_map[rs]["scope"][-1] - 1
        s += f"\tASSIGN\t{rs}_{temp}\t\t{dst}_{id_map[dst]['version_no']}"
        SymbolTable.insert(
            f"{dst}_{id_map[dst]['version_no']}"
        )  # Should I update the value?
        id_map[dst]["version_no"] += 1
        id_map[dst]["scope"][-1] = id_map[dst]["version_no"]

    if _print:
        print(s)
    return s


def decl_var(var, _print=True):
    s = ""
    if var in id_map:
        s += f"\tVAR\t\t\t{var}"
    else:
        SymbolTable.insert(var)

    if _print and len(s) > 0:
        print(s)
    return s


def decl_temp(val, val_type):
    global temp_var_no
    decl_var("t" + str(temp_var_no))
    assign("t" + str(temp_var_no), val)
    t = temp_var_no
    temp_var_no += 1
    return t


def modify_id_map(op):
    if op == "push":
        for i in id_map:
            id_map[i]["scope"].append(id_map[i]["version_no"])
    else:
        for i in id_map:
            id_map[i]["scope"].pop()


def p_for(p):
    """
    for :  FOR LPAREN assign SEMI cond SEMI unary RPAREN LBRACE new_scope statement RBRACE
    """
    p[0] = ("for", p[3], p[5], p[7], p[9], p[10], p[11])

    print("Deleting scope table")
    tables.append(stack.pop())
    tables[-1].name = "FOR"


def p_start(p):
    """
    start : statement_list
    """
    p[0] = p[1]


def p_while(p):
    """
    while :  WHILE gen_new_label new_tab LPAREN cond RPAREN LBRACE new_scope statement_list RBRACE delete_scope
    """
    p[0] = ("while", p[5], p[7], p[9], p[10])

    tables[-1].name = "WHILE"
    goto(label_stack[-1] + str(label_stack_no[-1] - 2))
    print_label()


def p_new_scope(p):
    """
    new_scope : empty
    """
    stack.append(Table())
    label_stack.append(label_stack[-1] + str(label_stack_no[-1]) + "_")
    label_stack_no.append(0)

    modify_id_map("push")


def p_delete_scope(p):
    """
    delete_scope : empty
    """
    # print("Deleting scope table")

    tables.append(stack.pop())
    label_stack.pop()
    label_stack_no.pop()

    modify_id_map("pop")


def p_if(p):
    """
    if : IF new_tab LPAREN cond RPAREN LBRACE new_scope statement_list RBRACE delete_scope optional
    """
    p[0] = ("if", p[4], p[6], p[8], p[9])
    # tables[-1].name = 'IF'

    print_label()


def p_new_tab(p):
    """
    new_tab : empty
    """
    p[0] = p[1]
    print("\t", end="")


def p_optional_1(p):
    """
    optional : empty
    """
    p[0] = p[1]


def p_optional(p):
    """
    optional : ELSE gen_goto gen_new_label LBRACE new_scope statement_list RBRACE delete_scope
    """
    p[0] = ("else", p[4], p[6], p[7])
    # tables[-1].name = 'ELSE'


def p_gen_goto(p):
    """
    gen_goto : empty
    """
    goto(label_stack[-1] + str(label_stack_no[-1] + 1))


def p_gen_new_label(p):
    """
    gen_new_label : empty
    """
    p[0] = p[1]
    print_label()


def p_switch(p):
    """
    switch : SWITCH LPAREN switch_expr RPAREN LBRACE labeled_statement_list RBRACE
    """
    p[0] = ("switch", p[3], p[5], p[6], p[7])
    print("l_comparisons:")
    # print cases here
    for case in cases_list:
        if case[0] == "case":
            try:
                temp = id_map[switch_expr]["scope"][-1] - 1
                print(f"\tEQ\t{switch_expr}_{temp}\t{case[1]}\t{case[2]}")
            except:
                print(f"\tEQ\t{switch_expr}\t{case[1]}\t{case[2]}")
        else:
            goto(f"{case[1]}")
    print("l_next_switch:")


def p_switch_expr(p):
    """
    switch_expr : ID
                    | ICONST
    """
    p[0] = p[1]

    global switch_expr
    if isDeclared(p[1][0]):
        switch_expr = p[1][0]
    else:
        displayNotDeclared(f"{p[1][0]}")

    goto("l_comparisons")


def p_labeled_statement_list(p):
    """
    labeled_statement_list : labeled_statement labeled_statement_list
    """
    p[0] = (p[1], p[2])


def p_labeled_statement_list_1(p):
    """
    labeled_statement_list : empty
    """
    p[0] = p[1]


def p_labeled_statement(p):
    """
    labeled_statement : CASE gen_new_label const_expr COLON new_scope statement_list delete_scope
    """
    p[0] = ("case", p[2], p[5])
    temp = label_stack_no[-1] - 1
    cases_list.append(("case", p[3], f"{label_stack[-1]}{temp}"))


def p_labeled_statement_1(p):
    """
    labeled_statement :  DEFAULT COLON gen_new_label new_scope statement_list delete_scope
    """
    p[0] = ("default", p[5])
    temp = label_stack_no[-1] - 1
    cases_list.append(("default", f"{label_stack[-1]}{temp}"))
    goto("l_next_switch")


def p_labeled_statement_3(p):
    """
    labeled_statement :  labeled_statement BREAK SEMI
    """
    p[0] = ("labeled_statement", p[1], p[3])
    goto("l_next_switch")


def p_const_expr(p):
    """
    const_expr : ICONST
                            | CCONST
    """
    p[0] = p[1]


def p_statement_list(p):
    """
    statement_list : statement statement_list
    """
    p[0] = (p[1], p[2])  # Doubtful about this


def p_statement_list_1(p):
    """
    statement_list : empty
    """
    p[0] = p[1]


def p_statement_5(p):
    """
    statement : unary
                            | assign
                            | declaration
                            | while
                            | if
                            | switch
    """
    p[0] = p[1]


def p_empty(p):
    "empty :"
    ...


def p_assign(p):
    """
    assign : ID EQUALS expr SEMI
    """
    p[0] = ("EXPRESSION CALCULATED", "=", p[1], p[3])

    if not isDeclared(p[1]):
        displayNotDeclared(p[1])

    if type(p[3]) == tuple:
        assign(p[1], p[3][0])
        stack[-1].update_val(p[1], _get_value(p[3][0]))
    elif p[3] not in id_map:
        assign(p[1], "t" + str(p[3]))
    else:
        assign(p[1], p[3])


def p_assign_1(p):
    """
    assign : ID EQUALS CCONST SEMI
    """
    p[0] = (p[1], p[3])

    if not isDeclared(p[1]):
        displayNotDeclared(p[1])
    else:
        assign(p[1], p[3])
        stack[-1].update_val(p[1], _get_value(p[3]))


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

    if p[1] in id_map:
        if isDeclared(p[1]):
            temp = id_map[p[1]]["scope"][-1] - 1
            t1 = f"{p[1]}_{temp}"
        else:
            temp = "\b" * 8
            displayNotDeclared(f"{p[1]}")
    else:
        t1 = p[1]

    if p[3] in id_map:
        if isDeclared(p[3]):
            temp = id_map[p[3]]["scope"][-1] - 1
            t2 = f"{p[3]}_{temp}"
        else:
            temp = "\b" * 8
            print(f"{temp}")
            displayNotDeclared(f"{p[3]}")
    else:
        t2 = p[3]

    try:
        print(
            "%s\t%s\t%s\t%s" % (p[2], t1, t2, label_stack[-1] + str(label_stack_no[-1]))
        )
        goto(label_stack[-1] + str(label_stack_no[-1] + 1))
        print("%s:" % (label_stack[-1] + str(label_stack_no[-1])))
        label_stack_no[-1] += 1
    except:
        ...


def p_cond_1(p):
    """
    cond : ID
    """
    p[0] = p[1]

    if p[1] in id_map:
        if isDeclared(p[1]):
            temp = id_map[p[1]]["scope"][-1] - 1
            t1 = f"{p[1]}_{temp}"
        else:
            temp = "\b" * 8
            print(f"{temp}")
            displayNotDeclared(f"{p[1]}")
    else:
        t1 = p[1]

    try:
        print("GT\t%s\t0\tl%s" % (t1, label_stack_no[-1]))
        goto(label_stack[-1] + str(label_stack_no[-1] + 1))
        print_label()
    except:
        ...


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
    declaration : types vee SEMI
                            | types arr SEMI
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


def p_vee_2(p):
    """
    vee : vee COMMA vee
    """
    p[0] = (p[1], ",", p[3])


def p_vee_1(p):
    """
    vee : ID
    """
    p[0] = p[1]

    try:
        stack[-1].insert(p[1], "")
        decl_var(p[1])

    except Exception:
        ...


def p_vee_4(p):
    """
    vee : init
    """
    p[0] = p[1]


def p_init_1(p):
    """
    init : ID EQUALS expr
    """
    p[0] = ("EXPRESSSION CALCULATED", "=", p[1], p[3])

    try:
        stack[-1].insert(p[1], "")
        decl_var(p[1])
        if type(p[3]) == tuple:
            assign(p[1], p[3][0])
            stack[-1].update_val(p[1], _get_value(p[3][0]))
        elif p[3] not in id_map:
            assign(p[1], "t" + str(p[3]))
        else:
            if isDeclared(p[3]):
                assign(p[1], p[3])
            else:
                displayNotDeclared(p[3])
    except Exception:
        print("Caught exception")


def p_init(p):
    """
    init : ID EQUALS CCONST
    """
    p[0] = ("=", p[1], p[3])

    try:
        stack[-1].insert(p[1], "")
        stack[-1].update_val(p[1], _get_value(p[3]))
        decl_var(p[1])
        assign(p[1], p[3])
    except Exception:
        ...


def p_arr(p):
    """
    arr : ID open_bracket
    """
    p[0] = p[1]
    try:
        stack[-1].insert(p[1], "")

        decl_var(p[1])
    except:
        ...


def p_open_bracket(p):
    """
    open_bracket : LBRACKET ICONST RBRACKET
                            | LBRACKET ICONST RBRACKET open_bracket
    """

    try:
        p[0] = (p[1], p[2], p[3], p[4])
    except:
        p[0] = (p[1], p[2], p[3])


def p_expr(p):
    """
    expr : expr PLUS term
            | expr MINUS term
    """
    global temp_var_no

    if type(p[1]) == type((1,)):  # ICONST or FCONST
        t1 = decl_temp(p[1][0], p[1][1])
        t1 = f"t{t1}"
    elif p[1] in id_map:  # ID
        if isDeclared(p[1]):
            temp = id_map[p[1]]["scope"][-1] - 1
            t1 = f"{p[1]}_{temp}"
        else:
            displayNotDeclared(p[1])
    else:
        t1 = f"t{p[1]}"

    if type(p[3]) == tuple:
        t2 = decl_temp(p[3][0], p[3][1])
        t2 = f"t{t2}"
    elif p[3] in id_map:
        if isDeclared(p[3]):
            temp = id_map[p[3]]["scope"][-1] - 1
            t2 = f"{p[3]}_{temp}"
        else:
            displayNotDeclared(p[3])
    else:
        t2 = f"t{p[3]}"

    try:
        if p[2] == "PLUS":
            decl_var(f"t{temp_var_no}")
            print(f"\tADD\t{t1}\t{t2}\tt{temp_var_no}")
            temp_var_no += 1
        elif p[2] == "MINUS":
            decl_var(f"t{temp_var_no}")
            print(f"\tSUB\t{t1}\t{t2}\tt{temp_var_no}")
            temp_var_no += 1
    except Exception:
        ...

    p[0] = str(temp_var_no - 1)


def p_expr_1(p):
    """
    expr : term
    """
    p[0] = p[1]


def p_term(p):
    """
    term : term TIMES factor
            | term DIVIDE factor
    """
    global temp_var_no

    p[0] = (p[1], p[3])
    if type(p[1]) == type((1,)):  # ICONST or FCONST
        t1 = decl_temp(p[1][0], p[1][1])
        t1 = f"t{t1}"
    elif p[1] in id_map:  # ID
        temp = id_map[p[1]]["scope"][-1] - 1
        t1 = f"{p[1]}_{temp}"
    else:
        t1 = f"t{p[1]}"

    if type(p[3]) == tuple:
        t2 = decl_temp(p[3][0], p[3][1])
        t2 = f"t{t2}"
    elif p[3] in id_map:
        temp = id_map[p[3]]["scope"][-1] - 1
        t2 = f"{p[3]}_{temp}"
    else:
        t2 = f"t{p[3]}"

    if p[2] == "TIMES":
        decl_var(f"t{temp_var_no}")
        print(f"\tMUL\t{t1}\t{t2}\tt{temp_var_no}")
        temp_var_no += 1

    elif p[2] == "DIVIDE":
        decl_var(f"t{temp_var_no}")
        print(f"\tDIV\t{t1}\t{t2}\tt{temp_var_no}")
        temp_var_no += 1

    p[0] = str(temp_var_no - 1)


def p_term_1(p):
    """
    term : factor
    """
    p[0] = p[1]


def p_factor(p):
    """
    factor : ID
    """
    p[0] = p[1]


def p_factor_1(p):
    """
    factor : ICONST
    """
    p[0] = (p[1], "INT")


def p_factor_2(p):
    """
    factor : FCONST
    """
    p[0] = (p[1], "FLOAT")


def p_error(p):
    if p:
        print("Syntax error in input!\t Line no:", p.lineno)
    else:
        print("Syntax error in input!")
        return
    while True:
        tok = parser.token()  # Get the next token
        if (
            not tok
            or tok.type == "SEMI"
            or tok.type == "RBRACE"
            or tok.type == "RPAREN"
        ):
            break
    parser.restart()


def display_all_tables():
    tables.append(stack.pop())
    while len(tables) > 0:
        t = tables.pop()
        t.display()


tokens_lines = list()


def get_token_line():
    global tokens_lines
    print(" ------------------------------------------------ 1st token lines ---------------------------------------------\n")
    print(tokens_lines)
    if tokens_lines != []:
        result = tokens_lines[0].strip()
        tokens_lines = tokens_lines[1:]
        print(" ------------------------------------------------ 2nd token lines ---------------------------------------------\n")
        print(tokens_lines)
        print(" ------------------------------------------------------- done ------------------------------------------------ \n")
        return result
    else:
        return tokens_lines


pa2_tokens = []


class PA2Lexer(object):
    def token(self):
        global pa2_tokens
        if pa2_tokens == []:
            return None
        (lineno, token_type, lexeme) = pa2_tokens[0]
        pa2_tokens = pa2_tokens[1:]
        tok = LexToken()
        tok.type = token_type
        tok.value = lexeme
        tok.lineno = lineno
        tok.lexpos = 0
        return tok


id_map = {}

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

        if token_type == "ID" and token_lexeme not in id_map:
            id_map[token_lexeme] = {
                "line_no": line_number,
                "scope": [0],
                "version_no": 0,
            }

        pa2_tokens = pa2_tokens + [(line_number, token_type.upper(), token_lexeme)]
    # print(pa2_tokens)

    pa2lexer = PA2Lexer()

    parser = yacc.yacc()
    ast = yacc.parse(lexer=pa2lexer)
    # print(ast)

    # display_all_tables()
    # SymbolTable.display()

    with open("symbol_table.pkl", "wb") as f:
        pickle.dump(SymbolTable, f)
    # print("Done!")
