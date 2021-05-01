from backend.parser import *

import backend.tokrules as tokrules
from backend.tokrules import tokens


def terminal_parser():
    argzparsi = argparse.ArgumentParser()
    argzparsi.add_argument(
        "-f", "--filename", help="path to the file containing the source code"
    )
    argzparsi.add_argument(
        "-c",
        "--cached",
        help="Use the source code cached in variable inside the same program",
        action="store_true",
    )
    return argzparsi.parse_args()


def u_getSourceCode():
    global cached_input
    if args.cached:
        if cached_input:
            return cached_input
        else:
            print(f"[!] There is no cached source code inside the program")
            print("\tPlease Edit the variable 'namedcached_input' ")
    try:
        filename = args.filename
        print(f"[i] Going to get source code from {filename}")
        file_h = open(filename, "r")
        return file_h.read()
    except:
        print("[!] No file path mentioned")
        exit(0)


args = terminal_parser()
lexer = lex.lex(module=tokrules)
lexer.input(u_getSourceCode())
token_list = u_getTokenList(lexer)
print(f"[i] List of Tokens generated: {token_list}\n")
pa2lexer = PA2Lexer(token_list)

parser = yacc.yacc()
ast = yacc.parse(lexer=pa2lexer)
print(ast)

display_all_tables()
