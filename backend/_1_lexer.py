import ply.lex as lex
import _0_tokrules as tokrules
import json
import ply.lex as lex
from termcolor import cprint

try:
    file_code = open("../test/demo.cpp", "r").read()
except:
    file_code = open("./test/phase1test1.cpp", "r").read()
lexer = lex.lex(module=tokrules)
lexer.input(file_code)


def getIfASCII(value_, type_):
    disallowed_type = ["ID", "SCONST", "ICONST", "FCONST"]
    if len(value_) == 1 and type_ not in disallowed_type:
        value_ = ord(value_)
    return value_


def getIfNumber(value_, type_):
    try:
        if type_ == "ICONST":
            return int(value_)
        if type_ == "FCONST":
            return float(value_)
    except:
        ...
    return value_


# Compute column.
# input is the input text string, token is a token instance
def find_column(input, token):
    line_start = input.rfind("\n", 0, token.lexpos) + 1
    first_col = (token.lexpos - line_start) + 1
    last_col = len(token.value) + first_col - 1
    return (first_col, last_col)


token_json = {"items": []}

# Tokenize
for tok in lexer:
    col_range = find_column(file_code, tok)
    tok.value = getIfASCII(tok.value, tok.type)
    tok.value = getIfNumber(tok.value, tok.type)
    json_item = [tok.type, tok.value, tok.lineno, tok.lexpos, col_range]
    token_json["items"].append(json_item)
    cprint(f"{tok}, Column Range: {col_range}", "green")


with open("symbol_table.json", "w") as f:
    json.dump(token_json, f)
