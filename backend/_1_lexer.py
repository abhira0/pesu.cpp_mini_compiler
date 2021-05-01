import ply.lex as lex
import .0_tokrules as tokrules

cached_code = """
// dfvdfjvndns dvhjsk  \vdsvvdvh\nvdev
int a;
void b;

"""
lexer = lex.lex(module=tokrules)
lexer.input(cached_code)
for tok in lexer.token():
    print(tok)
