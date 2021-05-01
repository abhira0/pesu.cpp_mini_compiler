import ply.lex as lex
import _0_tokrules as tokrules

source_code_path = "../sourceCode.txt"
file_code = open(source_code_path, "r").read()
lexer = lex.lex(module=tokrules)
lexer.input(file_code)

# Tokenize
for tok in lexer:
    print(tok)