import argparse
import json
import pickle
import sys

import pandas
import ply.lex as lex
import ply.yacc as yacc
import tabulate
from ply.lex import LexToken

from _0_tokrules import *

"""-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_"""

code_list = []


class utils:
    @staticmethod
    def display_table(dikt: dict, title: str, transpose: bool = True) -> None:
        df = pandas.DataFrame(dikt)
        df = df.transpose() if transpose else df
        if dikt:
            print(f"\t\t{title}")
        tabulated = tabulate.tabulate(
            df, headers="keys", tablefmt="pretty", showindex=False
        )
        cprint(tabulated, "green")

    @staticmethod
    def goto(text) -> None:
        global code_list
        code_list.append(f"\tGOTO\t\t\t{text}")
        # cprint(f"\tGOTO\t\t\t{text}", "cyan")

    @staticmethod
    def getActualValue(x):
        try:
            return int(x)
        except:
            ...
        try:
            return float(x)
        except:
            ...
        return x

    @staticmethod
    def isDeclared(var) -> bool:
        if var not in idm.dikt:
            return True

        i = len(Stack) - 1
        while i >= 0:
            if var in Stack[i].variables:
                return True
            i -= 1

        return False

    @staticmethod
    def printNotDeclared(var) -> None:
        wprint(f"{var} is not declared.")

    @staticmethod
    def print_label() -> None:
        global label_stack
        global label_stack_no
        global code_list
        # cprint(f"{label_stack[-1]}{label_stack_no[-1]}:", "cyan")
        code_list.append(f"{label_stack[-1]}{label_stack_no[-1]}:")
        label_stack_no[-1] += 1

    @staticmethod
    def assign(dst, rs) -> None:
        """if variable not in id_map then variable is a temp variable """
        s = ""
        global SymTab
        rs_flag = rs in idm.dikt
        dst_flag = dst in idm.dikt
        if (not rs_flag) and (not dst_flag):
            s += f"\tASSIGN\t{rs}\t\t{dst}"
            SymTab.insert(dst)
        elif (rs_flag) and (not dst_flag):
            temp = idm.dikt[rs]["scope"][-1] - 1
            s += f"\tASSIGN\t{rs}_{temp}\t\t{dst}"
            SymTab.insert(dst)
        elif (not rs_flag) and (dst_flag):
            s += f"\tASSIGN\t{rs}\t\t{dst}_{idm.dikt[dst]['version_no']}"
            SymTab.insert(f"{dst}_{idm.dikt[dst]['version_no']}")
            idm.dikt[dst]["version_no"] += 1
            idm.dikt[dst]["scope"][-1] = idm.dikt[dst]["version_no"]
        else:
            temp = idm.dikt[rs]["scope"][-1] - 1
            s += f"\tASSIGN\t{rs}_{temp}\t\t{dst}_{idm.dikt[dst]['version_no']}"
            SymTab.insert(
                f"{dst}_{idm.dikt[dst]['version_no']}"
            )  # Should I update the value?
            idm.dikt[dst]["version_no"] += 1
            idm.dikt[dst]["scope"][-1] = idm.dikt[dst]["version_no"]

        global code_list
        code_list.append(s)
        # cprint(s, "cyan")

    @staticmethod
    def decl_var(var) -> None:
        s = ""
        if var in idm.dikt:
            s += f"\tVAR\t\t\t{var}"
        else:
            SymTab.insert(var)

        if len(s) > 0:
            global code_list
            code_list.append(s)
            # cprint(s, "cyan")

    @staticmethod
    def decl_temp(val, val_type):
        global temp_var_no
        utils.decl_var("t" + str(temp_var_no))
        utils.assign("t" + str(temp_var_no), val)
        t = temp_var_no
        temp_var_no += 1
        return t

    @staticmethod
    def display_all_tables():
        global Tables
        global Stack
        Tables.append(Stack.pop())
        while len(Tables) > 0:
            t = Tables.pop()
            t.display()


class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def insert(self, var):
        if var not in self.symbols.keys():
            self.symbols[var] = {"name": var, "type": None, "value": None}

    def display(self):
        title = f"Symbol Table"
        utils.display_table(self.symbols, title)

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
            wprint(f"{var} has already been declared in line no. {line_no}")
            raise ValueError
        else:
            self.variables[var] = {
                "name": var,
                "type": "def_type",
                "value": None,
                "address": None,
                "lineno": idm.dikt[var]["line_no"],
                "code": 1,
            }  # 1->recently added, 0 otherwise
            self.variables[var]["address"] = hex(id(self.variables[var]["name"]))

    def display(self):
        title = f"Table for : {self.name} scope"
        utils.display_table(self.variables, title)

    def update_type(self, new_type):
        for key in self.variables.keys():
            if self.variables[key]["code"]:
                self.variables[key]["type"] = new_type

                if self.variables[key]["value"] != None and self.types[
                    new_type
                ] != type(self.variables[key]["value"]):
                    wprint(
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
            if not utils.isDeclared(var):
                utils.printNotDeclared(var)
            else:
                if self.get_val(new_val) == None:
                    raise Exception
                else:
                    self.set_val(var, self.get_val(new_val))
        except Exception:
            if not utils.isDeclared(var):
                utils.printNotDeclared(var)
            else:
                t = self.get_type(var)
                if t != "def_type" and self.types[t.upper()] != type(new_val):
                    wprint(f"Type of {var} does not match {new_val}!")
                self.set_val(var, new_val)

    def get_type(self, var):
        global Stack
        for i in range(len(Stack) - 1, -1, -1):
            if var in Stack[i].variables:
                return Stack[i].variables[var]["type"]

    def set_val(self, var, val):
        global Stack
        for i in range(len(Stack) - 1, -1, -1):
            if var in Stack[i].variables:
                Stack[i].variables[var]["value"] = val
                break

    def get_val(self, var):
        global Stack
        for i in range(len(Stack) - 1, -1, -1):
            if var in Stack[i].variables:
                return Stack[i].variables[var]["value"]


class IDMap:
    def __init__(self, symbol_table):
        self.dikt = {}
        for token in symbol_table["items"]:
            if token[0] == "ID":
                self.new_id(token[1], token[2])

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


Tables = []
Stack = [ScopeTable("GLOBAL")]
cases_list = []
SymTab = SymbolTable()
switch_expr = None
for_expr = False
label_stack = ["l"]
label_stack_no = [0]
temp_var_no = 0


""" ---------------------------------------------------------------------
    |   Grammer Rules with actions
    --------------------------------------------------------------------- """


def p_start(p):
    """
    start : INT MAIN LPAREN RPAREN LBRACE statement_list RBRACE
    """
    p[0] = p[6]


def p_for(p):
    """
    for :  FOR LPAREN check_for new_scope statement gen_new_label cond SEMI unary RPAREN LBRACE gen_new_label statement_list cond_label RBRACE uncheck_for delete_scope
    """
    p[0] = ("for", p[3], p[5], p[7], p[9], p[10], p[11])

    Tables[-1].name = "FOR"


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
    utils.print_label()


def p_cond_label(p):
    """
    cond_label : empty
    """
    utils.goto(label_stack[-1] + str(label_stack_no[-1] - 2))


def p_new_scope(p):
    """
    new_scope : empty
    """
    Stack.append(ScopeTable())
    label_stack.append(label_stack[-1] + str(label_stack_no[-1]) + "_")
    label_stack_no.append(0)

    idm.modify("push")


def p_delete_scope(p):
    """
    delete_scope : empty
    """

    Tables.append(Stack.pop())
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
    utils.print_label()


def p_switch(p):
    """
    switch : SWITCH LPAREN new_scope switch_expr RPAREN LBRACE labeled_statement_list RBRACE delete_scope
    """
    p[0] = ("switch", p[3], p[5], p[6], p[7])
    Tables[-1].name = "SWICTH"
    global code_list
    code_list.append("l_comparisons:")
    # cprint("l_comparisons:", "cyan")
    # print cases here
    for case in cases_list:
        if case[0] == "case":
            try:
                temp = idm.dikt[switch_expr]["scope"][-1] - 1
                code_list.append(f"\tEQ\t{switch_expr}_{temp}\t{case[1]}\t{case[2]}")
                # cprint(f"\tEQ\t{switch_expr}_{temp}\t{case[1]}\t{case[2]}", "cyan")
            except:
                code_list.append(f"\tEQ\t{switch_expr}\t{case[1]}\t{case[2]}")
                # cprint(f"\tEQ\t{switch_expr}\t{case[1]}\t{case[2]}", "cyan")
        else:
            utils.goto(f"{case[1]}")
    code_list.append("l_next_switch:")
    # cprint("l_next_switch:", "cyan")


def p_switch_expr(p):
    """
    switch_expr : ID
                    | ICONST
    """
    p[0] = p[1]

    global switch_expr
    if utils.isDeclared(p[1][0]):
        switch_expr = p[1][0]
    else:
        utils.printNotDeclared(f"{p[1][0]}")

    utils.goto("l_comparisons")


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
    Tables[-1].name = "SWITCH CASE"
    temp = label_stack_no[-1] - 1
    cases_list.append(("case", p[3], f"{label_stack[-1]}{temp}"))


def p_labeled_statement_1(p):
    """
    labeled_statement :  DEFAULT COLON gen_new_label new_scope statement_list delete_scope
    """
    p[0] = ("default", p[5])
    Tables[-1].name = "SWITCH DEF"
    temp = label_stack_no[-1] - 1
    cases_list.append(("default", f"{label_stack[-1]}{temp}"))
    utils.goto("l_next_switch")


def p_labeled_statement_2(p):
    """
    labeled_statement :  labeled_statement BREAK SEMI
    """
    p[0] = ("labeled_statement", p[1], p[3])
    utils.goto("l_next_switch")


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


def p_statement(p):
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

    if not utils.isDeclared(p[1]):
        utils.printNotDeclared(p[1])

    if type(p[3]) == tuple:
        utils.assign(p[1], p[3][0])
        Stack[-1].update_val(p[1], utils.getActualValue(p[3][0]))
    elif p[3] not in idm.dikt:
        utils.assign(p[1], "t" + str(p[3]))
    else:
        utils.assign(p[1], p[3])


def p_assign_1(p):
    """
    assign : ID EQUALS CCONST SEMI
    """
    p[0] = (p[1], p[3])

    if not utils.isDeclared(p[1]):
        utils.printNotDeclared(p[1])
    else:
        utils.assign(p[1], p[3])
        Stack[-1].update_val(p[1], utils.getActualValue(p[3]))


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
    global code_list

    if p[1] in idm.dikt:
        if utils.isDeclared(p[1]):
            temp = idm.dikt[p[1]]["scope"][-1] - 1
            t1 = f"{p[1]}_{temp}"
        else:
            temp = "\b" * 8
            utils.printNotDeclared(f"{p[1]}")
    else:
        t1 = p[1]

    if p[3] in idm.dikt:
        if utils.isDeclared(p[3]):
            temp = idm.dikt[p[3]]["scope"][-1] - 1
            t2 = f"{p[3]}_{temp}"
        else:
            temp = "\b" * 8
            code_list.append(f"{temp}")
            # cprint(f"{temp}", "cyan")
            utils.printNotDeclared(f"{p[3]}")
    else:
        t2 = p[3]

    try:
        global for_expr
        if for_expr == False:
            code_list.append(
                "\t%s\t%s\t%s\t%s"
                % (sym_map[p[2]], t1, t2, label_stack[-1] + str(label_stack_no[-1]))
            )
            # cprint(
            #     "\t%s\t%s\t%s\t%s"
            #     % (sym_map[p[2]], t1, t2, label_stack[-1] + str(label_stack_no[-1])),
            #     "cyan",
            # )
            utils.goto(label_stack[-1] + str(label_stack_no[-1] + 1))
            code_list.append("%s:" % (label_stack[-1] + str(label_stack_no[-1])))
            # cprint("%s:" % (label_stack[-1] + str(label_stack_no[-1])), "cyan")
            label_stack_no[-1] += 1
        elif for_expr == True:
            code_list.append(
                "\t%s\t%s\t%s\t%s"
                % (
                    sym_map[p[2]],
                    t1,
                    t2,
                    label_stack[-1] + str(label_stack_no[-1] + 1),
                )
            )
            # cprint(
            #     "\t%s\t%s\t%s\t%s"
            #     % (
            #         sym_map[p[2]],
            #         t1,
            #         t2,
            #         label_stack[-1] + str(label_stack_no[-1] + 1),
            #     ),
            #     "cyan",
            # )
            utils.goto(label_stack[-1] + str(label_stack_no[-1] + 2))
            code_list.append("%s:" % (label_stack[-1] + str(label_stack_no[-1])))
            # cprint("%s:" % (label_stack[-1] + str(label_stack_no[-1])), "cyan")
            label_stack_no[-1] += 1
    except:
        ...


def p_cond_1(p):
    """
    cond : ID
    """
    p[0] = p[1]
    global code_list
    if p[1] in idm.dikt:
        if utils.isDeclared(p[1]):
            temp = idm.dikt[p[1]]["scope"][-1] - 1
            t1 = f"{p[1]}_{temp}"
        else:
            temp = "\b" * 8
            code_list.append(f"{temp}")
            # cprint(f"{temp}", "cyan")
            utils.printNotDeclared(f"{p[1]}")
    else:
        t1 = p[1]

    try:
        code_list.append("GT\t%s\t0\tl%s" % (t1, label_stack_no[-1]))
        # cprint("GT\t%s\t0\tl%s" % (t1, label_stack_no[-1]), "cyan")
        utils.goto(label_stack[-1] + str(label_stack_no[-1] + 1))
        utils.print_label()
    except:
        ...


def p_unary_pre(p):
    """
    unary : PLUSPLUS ID
       | MINUSMINUS ID
    """
    global code_list
    if p[1] == "++":
        p[0] = ("PREINC", "++", p[2])
        code_list.append(f"\PREINC\t\t\t{p[2]}")
        # cprint(f"\PREINC\t\t\t{p[2]}", "cyan")
    elif p[1] == "--":
        p[0] = ("PREDEC", "--", p[2])
        code_list.append(f"\PREDEC\t\t\t{p[2]}")
        # cprint(f"\PREDEC\t\t\t{p[2]}", "cyan")
    utils.goto(label_stack[-1] + str(label_stack_no[-1] - 2))


def p_unary_post(p):
    """
    unary : ID PLUSPLUS
       | ID MINUSMINUS
    """
    global code_list
    if p[2] == "++":
        p[0] = ("POSTINC", "++", p[1])
        code_list.append(f"\tPOSTINC\t\t\t{p[1]}")
        # cprint(f"\tPOSTINC\t\t\t{p[1]}", "cyan")
    elif p[2] == "--":
        p[0] = ("POSTDEC", "--", p[1])
        code_list.append(f"\tPOSTDEC\t\t\t{p[1]}")
        # cprint(f"\tPOSTDEC\t\t\t{p[1]}", "cyan")
    utils.goto(label_stack[-1] + str(label_stack_no[-1] - 2))


def p_declaration(p):
    """
    declaration : types vee SEMI
                            | types arr SEMI
    """
    p[0] = (p[2], p[1])
    # Update the types of the above declared variables
    Stack[-1].update_type(p[1])


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


def p_vee_1(p):
    """
    vee : vee COMMA vee
    """
    p[0] = (p[1], ",", p[3])


def p_vee_2(p):
    """
    vee : ID
    """
    p[0] = p[1]

    try:
        Stack[-1].insert(p[1], "")
        utils.decl_var(p[1])

    except Exception:
        ...


def p_vee_3(p):
    """
    vee : init
    """
    p[0] = p[1]


def p_init(p):
    """
    init : ID EQUALS expr
    """
    p[0] = ("EXPRESSSION CALCULATED", "=", p[1], p[3])

    try:
        Stack[-1].insert(p[1], "")
        utils.decl_var(p[1])
        if type(p[3]) == tuple:
            utils.assign(p[1], p[3][0])
            Stack[-1].update_val(p[1], utils.getActualValue(p[3][0]))
        elif p[3] not in idm.dikt:
            utils.assign(p[1], "t" + str(p[3]))
        else:
            if utils.isDeclared(p[3]):
                utils.assign(p[1], p[3])
            else:
                utils.printNotDeclared(p[3])
    except Exception:
        wprint("Caught exception")


def p_init_1(p):
    """
    init : ID EQUALS CCONST
    """
    p[0] = ("=", p[1], p[3])

    try:
        Stack[-1].insert(p[1], "")
        Stack[-1].update_val(p[1], utils.getActualValue(p[3]))
        utils.decl_var(p[1])
        utils.assign(p[1], p[3])
    except Exception:
        ...


def p_arr(p):
    """
    arr : ID open_bracket
    """
    p[0] = p[1]
    try:
        Stack[-1].insert(p[1], "")

        utils.decl_var(p[1])
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
    global code_list
    if type(p[1]) == type((1,)):  # ICONST or FCONST
        t1 = utils.decl_temp(p[1][0], p[1][1])
        t1 = f"t{t1}"
    elif p[1] in idm.dikt:  # ID
        if utils.isDeclared(p[1]):
            temp = idm.dikt[p[1]]["scope"][-1] - 1
            t1 = f"{p[1]}_{temp}"
        else:
            utils.printNotDeclared(p[1])
    else:
        t1 = f"t{p[1]}"

    if type(p[3]) == tuple:
        t2 = utils.decl_temp(p[3][0], p[3][1])
        t2 = f"t{t2}"
    elif p[3] in idm.dikt:
        if utils.isDeclared(p[3]):
            temp = idm.dikt[p[3]]["scope"][-1] - 1
            t2 = f"{p[3]}_{temp}"
        else:
            utils.printNotDeclared(p[3])
    else:
        t2 = f"t{p[3]}"

    try:

        if p[2] == "+":
            utils.decl_var(f"t{temp_var_no}")
            code_list.append(f"\tADD\t{t1}\t{t2}\tt{temp_var_no}")
            # cprint(f"\tADD\t{t1}\t{t2}\tt{temp_var_no}", "cyan")
            temp_var_no += 1
        elif p[2] == "-":
            utils.decl_var(f"t{temp_var_no}")
            code_list.append(f"\tSUB\t{t1}\t{t2}\tt{temp_var_no}")
            # cprint(f"\tSUB\t{t1}\t{t2}\tt{temp_var_no}", "cyan")
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
    global code_list
    p[0] = (p[1], p[3])
    if type(p[1]) == type((1,)):  # ICONST or FCONST
        t1 = utils.decl_temp(p[1][0], p[1][1])
        t1 = f"t{t1}"
    elif p[1] in idm.dikt:  # ID
        temp = idm.dikt[p[1]]["scope"][-1]
        t1 = f"{p[1]}_{temp}"
    else:
        t1 = f"t{p[1]}"
    # print(p[1], p[2], p[3])
    if type(p[3]) == tuple:
        t2 = utils.decl_temp(p[3][0], p[3][1])
        t2 = f"t{t2}"
    elif p[3] in idm.dikt:
        temp = idm.dikt[p[3]]["scope"][-1]
        t2 = f"{p[3]}_{temp}"
    else:
        t2 = f"t{p[3]}"

    if p[2] == "*":
        utils.decl_var(f"t{temp_var_no}")
        code_list.append(f"\tMUL\t{t1}\t{t2}\tt{temp_var_no}")
        # cprint(f"\tMUL\t{t1}\t{t2}\tt{temp_var_no}", "cyan")
        temp_var_no += 1

    elif p[2] == "/":
        utils.decl_var(f"t{temp_var_no}")
        code_list.append(f"\tDIV\t{t1}\t{t2}\tt{temp_var_no}")
        # cprint(f"\tDIV\t{t1}\t{t2}\tt{temp_var_no}", "cyan")
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
        wprint(f"Syntax error in input!\t line no: {p.lineno}")
    else:
        wprint("Syntax error in input!")
        return
    while True:
        tok = parser.token()  # Next token
        break_point = ["SEMI", "RBRACE", "RPAREN"]
        if not tok or tok.type in break_point:
            break
    parser.restart()


"""-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_"""

# import _1_lexer
if __name__ == "__main__":
    with open("./p2_symbol_table.json") as f:
        symbol_table = json.load(f)

    idm = IDMap(symbol_table)
    # Parsing
    parser = yacc.yacc()
    ast = yacc.parse(lexer=CustomLexer())
    # Display 3 address code
    for i in code_list:
        cprint(i, "cyan")
    # Display tables
    utils.display_all_tables()
    SymTab.display()
    # Display AST
    print("ABSTRACT SYNTAX TREE : ", end="")
    cprint(ast, "green")
    # Save outputs
    with open("3code.txt", "w") as f:
        for i in code_list:
            f.write(i + "\n")
    with open("symbol_table.pkl", "wb") as f:
        pickle.dump(SymTab, f)
