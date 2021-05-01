import argparse
import pickle
import sys

import ply.lex as lex
import ply.yacc as yacc
from ply.lex import LexToken

from .tokrules import *

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


def display_all_tables():
    tables.append(stack.pop())
    while len(tables) > 0:
        t = tables.pop()
        t.display()


def get_token_line(token):
    if len(token) == 3:
        return 3
    elif len(token) == 2:
        return 2


def u_getTokenList(lexer):
    token_list = []
    for tok in lexer:
        flag = tok.type in ["ID", "TYPEID", "ICONST", "FCONST", "SCONST", "CCONST"]
        tok_value = str(tok.value) if flag else str(tok.type).upper()
        token_list.append((str(tok.lineno), str(tok.type), tok_value))
    return token_list


class PA2Lexer(object):
    def __init__(self, token_list) -> None:
        self.token_list = token_list

    def token(self):
        if self.token_list == []:
            return None
        (line, token_type, lexeme) = self.token_list[0]
        self.token_list = self.token_list[1:]
        tok = lex.LexToken()
        tok.type = token_type
        tok.value = lexeme
        tok.lineno = line
        tok.lexpos = 0
        return tok
