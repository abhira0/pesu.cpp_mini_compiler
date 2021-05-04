import argparse
import json
import pickle
import sys, pandas, tabulate

import ply.lex as lex
import ply.yacc as yacc
from ply.lex import LexToken
from _0_tokrules import *

"""-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_"""


class utils:
    @staticmethod
    def dashedLine(length: int = 25) -> None:
        print("-" * length)

    def display_table(dikt: dict, transpose: bool = True) -> None:
        df = pandas.DataFrame(dikt)
        df = df.transpose() if transpose else df
        print(tabulate.tabulate(df, headers="keys", tablefmt="pretty", showindex=False))


class ClassSymbolTable:
    def __init__(self):
        self.symbols = {}

    def insert(self, var):
        if var not in self.symbols.keys():
            self.symbols[var] = {"name": var, "type": None, "value": None}

    def display(self):
        utils.display_table(self.symbols)

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


class ScopeTable:
    def __init__(self, name=""):
        self.variables = {}
        self.name = name
        self.types = {
            "INT": type(int()),
            "FLOAT": type(float()),
            "CHAR": type(str()),
            "int": type(int()),
            "float": type(float()),
            "char": type(str()),
        }

    def insert(self, var, var_type):
        if var in self.variables.keys():
            line_no = idm.dikt[var]["line_no"]
            wprint(f"{var} has already been declared in Line no. {line_no}")
            raise ValueError
        else:
            self.variables[var] = {
                "name": var,
                "type": "Default_type",
                "value": None,
                "address": None,
                "lineno": idm.dikt[var]["line_no"],
                "code": 1,
            }  # 1->recently added, 0 otherwise
            self.variables[var]["address"] = hex(id(self.variables[var]["name"]))

    def display(self):
        utils.display_table(self.variables)

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
                if t != "Default_type" and self.types[t.upper()] != type(new_val):
                    print(f"Type of {var} does not match {new_val}!")
                set_val(var, new_val)


tables = []
stack = [ScopeTable("GLOBAL")]
label_stack = ["l"]
label_stack_no = [0]
switch_expr = None
cases_list = []
SymbolTable = ClassSymbolTable()
for_expr = False
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
    if var not in idm.dikt:
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


def goto(text, verbose: bool = True):
    s = f"\tGOTO\t\t\t{text}"
    print(s) if verbose else None
    return s


def assign(dst, rs, verbose=True):
    s = ""
    # variable not in id_map => variable is a temp variable
    if rs not in idm.dikt and dst not in idm.dikt:
        s += f"\tASSIGN\t{rs}\t\t{dst}"
        SymbolTable.insert(dst)
    elif rs in idm.dikt and dst not in idm.dikt:
        temp = idm.dikt[rs]["scope"][-1] - 1
        s += f"\tASSIGN\t{rs}_{temp}\t\t{dst}"
        SymbolTable.insert(dst)
    elif rs not in idm.dikt and dst in idm.dikt:
        s += f"\tASSIGN\t{rs}\t\t{dst}_{idm.dikt[dst]['version_no']}"
        SymbolTable.insert(f"{dst}_{idm.dikt[dst]['version_no']}")
        idm.dikt[dst]["version_no"] += 1
        idm.dikt[dst]["scope"][-1] = idm.dikt[dst]["version_no"]
    else:
        temp = idm.dikt[rs]["scope"][-1] - 1
        s += f"\tASSIGN\t{rs}_{temp}\t\t{dst}_{idm.dikt[dst]['version_no']}"
        SymbolTable.insert(
            f"{dst}_{idm.dikt[dst]['version_no']}"
        )  # Should I update the value?
        idm.dikt[dst]["version_no"] += 1
        idm.dikt[dst]["scope"][-1] = idm.dikt[dst]["version_no"]
    # SymbolTable.display()

    if verbose:
        print(s)
    return s


def decl_var(var, verbose=True):
    s = ""
    if var in idm.dikt:
        s += f"\tVAR\t\t\t{var}"
    else:
        SymbolTable.insert(var)

    if verbose and len(s) > 0:
        print(s)
    return s


def decl_temp(val, val_type):
    global temp_var_no
    decl_var("t" + str(temp_var_no))
    assign("t" + str(temp_var_no), val)
    t = temp_var_no
    temp_var_no += 1
    return t


""" ---------------------------------------------------------------------
    |   Grammer Rules with actions
    --------------------------------------------------------------------- """


def p_start(p):
    """
    start : INT MAIN LPAREN RPAREN LBRACE statement_list RBRACE
    """
    p[0] = p[4]


def p_for(p):
    """
    for :  FOR LPAREN check_for new_scope statement gen_new_label cond SEMI unary RPAREN LBRACE gen_new_label statement_list cond_label RBRACE uncheck_for delete_scope
    """
    p[0] = ("for", p[3], p[5], p[7], p[9], p[10], p[11])

    tables[-1].name = "FOR"


def p_check_for(p):
    """
    check_for : empty
    """
    global for_expr
    for_expr = True


def p_uncheck_for(p):
    """
    uncheck_for : empty
    """
    global for_expr
    for_expr = False
    print_label()


def p_cond_label(p):
    """
    cond_label : empty
    """
    goto(label_stack[-1] + str(label_stack_no[-1] - 2))


def p_new_scope(p):
    """
    new_scope : empty
    """
    stack.append(ScopeTable())
    label_stack.append(label_stack[-1] + str(label_stack_no[-1]) + "_")
    label_stack_no.append(0)

    idm.modify("push")


def p_delete_scope(p):
    """
    delete_scope : empty
    """

    tables.append(stack.pop())
    label_stack.pop()
    label_stack_no.pop()

    idm.modify("pop")


def p_new_tab(p):
    """
    new_tab : empty
    """
    p[0] = p[1]
    print("\t", end="")


def p_gen_new_label(p):
    """
    gen_new_label : empty
    """
    p[0] = p[1]
    print_label()


def p_switch(p):
    """
    switch : SWITCH LPAREN new_scope switch_expr RPAREN LBRACE labeled_statement_list RBRACE delete_scope
    """
    p[0] = ("switch", p[3], p[5], p[6], p[7])
    print("l_comparisons:")
    # print cases here
    for case in cases_list:
        if case[0] == "case":
            try:
                temp = idm.dikt[switch_expr]["scope"][-1] - 1
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
                            | for
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
    elif p[3] not in idm.dikt:
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
    sym_map = {"<=": "LE", "<": "LT", ">=": "GE", ">": "GT", "==": "EQ", "!=": "NE"}
    if p[2] == "<=":
        p[0] = ("CONDI", "<=", p[1], p[3])
    elif p[2] == "<":
        p[0] = ("CONDI", "<", p[1], p[3])
    elif p[2] == ">=":
        p[0] = ("CONDI", ">=", p[1], p[3])
    elif p[2] == ">":
        p[0] = ("CONDI", ">", p[1], p[3])
    elif p[2] == "==":
        p[0] = ("CONDI", "==", p[1], p[3])
    elif p[2] == "!=":
        p[0] = ("CONDI", "!=", p[1], p[3])

    if p[1] in idm.dikt:
        if isDeclared(p[1]):
            temp = idm.dikt[p[1]]["scope"][-1] - 1
            t1 = f"{p[1]}_{temp}"
        else:
            temp = "\b" * 8
            displayNotDeclared(f"{p[1]}")
    else:
        t1 = p[1]

    if p[3] in idm.dikt:
        if isDeclared(p[3]):
            temp = idm.dikt[p[3]]["scope"][-1] - 1
            t2 = f"{p[3]}_{temp}"
        else:
            temp = "\b" * 8
            print(f"{temp}")
            displayNotDeclared(f"{p[3]}")
    else:
        t2 = p[3]

    try:
        global for_expr
        if for_expr == False:
            print(
                "\t%s\t%s\t%s\t%s"
                % (sym_map[p[2]], t1, t2, label_stack[-1] + str(label_stack_no[-1]))
            )
            goto(label_stack[-1] + str(label_stack_no[-1] + 1))
            print("%s:" % (label_stack[-1] + str(label_stack_no[-1])))
            label_stack_no[-1] += 1
        elif for_expr == True:
            print(
                "\t%s\t%s\t%s\t%s"
                % (sym_map[p[2]], t1, t2, label_stack[-1] + str(label_stack_no[-1] + 1))
            )
            goto(label_stack[-1] + str(label_stack_no[-1] + 2))
            print("%s:" % (label_stack[-1] + str(label_stack_no[-1])))
            label_stack_no[-1] += 1
    except:
        ...


def p_cond_1(p):
    """
    cond : ID
    """
    p[0] = p[1]

    if p[1] in idm.dikt:
        if isDeclared(p[1]):
            temp = idm.dikt[p[1]]["scope"][-1] - 1
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
    if p[1] == "++":
        p[0] = ("PREINC", "++", p[2])
        print(f"\PREINC\t\t\t{p[2]}")
    elif p[1] == "--":
        p[0] = ("PREDEC", "--", p[2])
        print(f"\PREDEC\t\t\t{p[2]}")
    goto(label_stack[-1] + str(label_stack_no[-1] - 2))


def p_unary_post(p):
    """
    unary : ID PLUSPLUS
       | ID MINUSMINUS
    """
    if p[2] == "++":
        p[0] = ("POSTINC", "++", p[1])
        print(f"\tPOSTINC\t\t\t{p[1]}")
    elif p[2] == "--":
        p[0] = ("POSTDEC", "--", p[1])
        print(f"\tPOSTDEC\t\t\t{p[1]}")
    goto(label_stack[-1] + str(label_stack_no[-1] - 2))


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
        elif p[3] not in idm.dikt:
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
    elif p[1] in idm.dikt:  # ID
        if isDeclared(p[1]):
            temp = idm.dikt[p[1]]["scope"][-1] - 1
            t1 = f"{p[1]}_{temp}"
        else:
            displayNotDeclared(p[1])
    else:
        t1 = f"t{p[1]}"

    if type(p[3]) == tuple:
        t2 = decl_temp(p[3][0], p[3][1])
        t2 = f"t{t2}"
    elif p[3] in idm.dikt:
        if isDeclared(p[3]):
            temp = idm.dikt[p[3]]["scope"][-1] - 1
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
    elif p[1] in idm.dikt:  # ID
        temp = idm.dikt[p[1]]["scope"][-1] - 1
        t1 = f"{p[1]}_{temp}"
    else:
        t1 = f"t{p[1]}"

    if type(p[3]) == tuple:
        t2 = decl_temp(p[3][0], p[3][1])
        t2 = f"t{t2}"
    elif p[3] in idm.dikt:
        temp = idm.dikt[p[3]]["scope"][-1] - 1
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


class CustomLexer(object):
    def __init__(self):
        self.var_token_gen = self.token_gen()

    def token_gen(self):
        for token in symbol_table["items"]:
            lextoken_obj = LexToken()
            lextoken_obj.type = token[0]
            lextoken_obj.value = token[1]
            lextoken_obj.lineno = token[2]
            lextoken_obj.lexpos = token[3]
            yield lextoken_obj

    def token(self):
        try:
            ret_var = next(self.var_token_gen)
        except StopIteration:
            ret_var = None
        return ret_var


class IDMap:
    dikt = {}

    def new_id(self, tok_val, line_no: int, scope: list = [0], version_no: int = 0):
        if tok_val not in self.dikt:
            self.dikt[tok_val] = {
                "line_no": line_no,
                "scope": scope,
                "version_no": version_no,
            }

    def modify(self, operation):
        for i in self.dikt:
            if operation == "push":
                self.dikt[i]["scope"].append(self.dikt[i]["version_no"])
            elif operation == "pop":
                self.dikt[i]["scope"].pop()

    def __str__(self):
        return f"IDMap Dictionary: {str(self.dikt)}"


# import _1_lexer

idm = IDMap()
idm.dikt = {}
if __name__ == "__main__":
    with open("./symbol_table.json") as f:
        symbol_table = json.load(f)
    for token in symbol_table["items"]:
        if token[0] == "ID":
            idm.new_id(token[1], token[2])
    parser = yacc.yacc()
    ast = yacc.parse(lexer=CustomLexer())

    print(ast)
