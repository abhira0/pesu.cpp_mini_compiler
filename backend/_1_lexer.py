import ply.lex as lex
import _0_tokrules as tokrules

try:
    file_code = open("../sourceCode.txt", "r").read()
except:
    file_code = open("./sourceCode.txt", "r").read()
lexer = lex.lex(module=tokrules)
lexer.input(file_code)


def getIfASCII(tok):
    value = tok.value
    if len(value) == 1 and tok.type not in [
        "ID",
        "RCONST",
        "ICONST",
        "FCONST",
        "CCONST",
    ]:
        tok.value = ord(tok.value)
    return tok


# Compute column.
#     input is the input text string
#     token is a token instance
def find_column(input, token):
    line_start = input.rfind("\n", 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


# Tokenize
for tok in lexer:
    print(getIfASCII(tok), find_column(file_code, tok))
