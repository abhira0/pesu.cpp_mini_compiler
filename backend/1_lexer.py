import ply.lex as lex

cached_code = r"""
// dfvdfjvndns dvhjsk  \vdsvvdvh\nvdev
int a;
void b;

"""
lexer = lex.lex()
lexer.input(cached_code)
while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)
