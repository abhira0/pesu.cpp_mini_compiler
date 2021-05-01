import ply.lex as lex
import _0_tokrules as tokrules

try:
    file_code = open("../sourceCode.txt", "r").read()
except:
    file_code = open("./sourceCode.txt", "r").read()
lexer = lex.lex(module=tokrules)
lexer.input(file_code)

# Tokenize
for tok in lexer:
    print(tok)