# Reserved words
reserved = (
    ("AUTO", "BREAK", "CASE", "CHAR", "CONST", "CONTINUE", "DEFAULT", "DO")
    + ("DOUBLE", "ELSE", "ENUM" "EXTERN", "FLOAT", "FOR", "GOTO", "IF")
    + ("INT", "LONG", "REGISTER", "RETURN", "SHORT", "SIGNED", "SIZEOF", "STATIC")
    + ("STRUCT", "SWITCH", "TYPEDEF", "UNION", "UNSIGNED", "VOID", "VOLATILE", "WHILE")
    + ("PRINTF", "COUT")
)

reserved_map = {}
for r in reserved:
    reserved_map[r.lower()] = r
tokens = (
    reserved
    # literals
    + ("ID", "TYPEID", "ICONST", "FCONST", "SCONST", "CCONST")
    + ("PLUS", "MINUS", "TIMES", "DIVIDE", "MOD", "OR", "AND", "NOT", "XOR", "LSHIFT")
    # Operators
    + ("RSHIFT", "LOR", "LAND", "LNOT", "LT", "LE", "GT", "GE", "EQ", "NE")
    # Assignment
    + ("EQUALS", "TIMESEQUAL", "DIVEQUAL", "MODEQUAL", "PLUSEQUAL", "MINUSEQUAL")
    + ("LSHIFTEQUAL", "RSHIFTEQUAL", "ANDEQUAL", "XOREQUAL", "OREQUAL")
    # Increment/decrement
    + ("PLUSPLUS", "MINUSMINUS")
    # Structure dereference
    + ("ARROW",)
    # Conditional operator
    + ("CONDOP",)
    # Delimeters
    + ("LPAREN", "RPAREN", "LBRACKET", "RBRACKET", "LBRACE", "RBRACE")
    + ("COMMA", "PERIOD", "SEMI", "COLON")
    # Ellipsis (...)
    + ("ELLIPSIS",)
)

# A string containing ignored characters (spaces and tabs)
t_ignore = " \t\x0c"


# Comments
def t_ignore_comment(t):
    r"/\*(.|\n)*?\*/"
    t.lexer.lineno += t.value.count("\n")
    print("-" * 50)


def t_ignore_single_line_comment(t):
    r"//.*"
    t.lexer.lineno += t.value.count("\n")


# Operators
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_MOD = r"%"
t_OR = r"\|"
t_AND = r"&"
t_NOT = r"~"
t_XOR = r"\^"
t_LSHIFT = r"<<"
t_RSHIFT = r">>"
t_LOR = r"\|\|"
t_LAND = r"&&"
t_LNOT = r"!"
t_LT = r"<"
t_GT = r">"
t_LE = r"<="
t_GE = r">="
t_EQ = r"=="
t_NE = r"!="

# Assignment operators

t_EQUALS = r"="
t_TIMESEQUAL = r"\*="
t_DIVEQUAL = r"/="
t_MODEQUAL = r"%="
t_PLUSEQUAL = r"\+="
t_MINUSEQUAL = r"-="
t_LSHIFTEQUAL = r"<<="
t_RSHIFTEQUAL = r">>="
t_ANDEQUAL = r"&="
t_OREQUAL = r"\|="
t_XOREQUAL = r"\^="

# Increment/decrement
t_PLUSPLUS = r"\+\+"
t_MINUSMINUS = r"--"

# ->
t_ARROW = r"->"

# ?
t_CONDOP = r"\?"

# Delimeters
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_COMMA = r","
t_PERIOD = r"\."
t_SEMI = r";"
t_COLON = r":"
t_ELLIPSIS = r"\.\.\."

# Integer literal
t_ICONST = r"\d+([uU]|[lL]|[uU][lL]|[lL][uU])?"

# Floating literal
t_FCONST = r"((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?"

# String literal
t_SCONST = r"\"([^\\\n]|(\\.))*?\""

# Character constant 'c' or L'c'
t_CCONST = r"(L)?\'([^\\\n]|(\\.))*?\'"


# Identifiers
def t_ID(t):
    r"[A-Za-z_][\w_]*"
    # get() returns the value of the key if present. If not, return "ID"
    t.type = reserved_map.get(t.value, "ID")
    return t


# Defining a rule so we can track line numbers
def t_NEWLINE(t):
    r"\n+"
    t.lexer.lineno += t.value.count("\n")


# Error handling rule for lexer
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Preprocessor directive (ignored)
def t_preprocessor(t):
    r"\#(.)*?\n"
    t.lexer.lineno += 1
