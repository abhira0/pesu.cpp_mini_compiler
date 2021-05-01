import ply.lex as lex
import _0_tokrules as tokrules

cached_code = r"""// dfvdfjvndns dvhjsk  \vdsvvdvh\nvdev
int a;
void b;

"""


file_code = open("../sourceCode.txt", "r").read()
cached_code = file_code

lexer = lex.lex(module=tokrules)
lexer.input(cached_code)

for tok in lexer:
    print(tok)