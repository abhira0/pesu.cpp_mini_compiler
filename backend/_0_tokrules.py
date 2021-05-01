"""
All the token regex and rules are specified here.
"""

""" ---------------------------------------------------------------------
    |   List of reserved words and tokens
    --------------------------------------------------------------------- """

# Reserved words
reserved = (
    ("AUTO", "BREAK", "CASE", "CHAR", "CONST", "CONTINUE", "DEFAULT", "DO", "DOUBLE")
    + ("ELSE", "ENUM", "EXTERN", "FLOAT", "FOR", "GOTO", "IF", "INT", "LONG")
    + ("REGISTER", "RETURN", "SHORT", "SIGNED", "SIZEOF", "STATIC", "STRUCT", "SWITCH")
    + ("TYPEDEF", "UNION", "UNSIGNED", "VOID", "VOLATILE", "WHILE", "PRINTF")
)

# List of token names. This is always required
# The tokens list is also used by the parser.py module to identify terminals.
tokens = (
    reserved
    # Literals
    + ("ID", "TYPEID", "ICONST", "FCONST", "SCONST", "CCONST")
    # Operators (+, -, *, /, %, |, &, ~, ^, <<)
    + ("PLUS", "MINUS", "TIMES", "DIVIDE", "MOD", "OR", "AND", "NOT", "XOR", "LSHIFT")
    # Operators (>>, ||, &&, !, <, <=, >, >=, ==, !=)
    + ("RSHIFT", "LOR", "LAND", "LNOT", "LT", "LE", "GT", "GE", "EQ", "NE")
    # Assignment (=, *=, /=, %=, +=, -=)
    + ("EQUALS", "TIMESEQUAL", "DIVEQUAL", "MODEQUAL", "PLUSEQUAL", "MINUSEQUAL")
    # Assignment (-=, <<=, >>=, &=, ^=, |=)
    + ("LSHIFTEQUAL", "RSHIFTEQUAL", "ANDEQUAL", "XOREQUAL", "OREQUAL")
    # Increment/decrement (++, --)
    + ("PLUSPLUS", "MINUSMINUS")
    # Structure dereference (->)
    + ("ARROW",)
    # Conditional operator (?)
    + ("CONDOP",)
    # Delimeters ( ) [ ] { } , . ; :
    + ("LPAREN", "RPAREN", "LBRACKET", "RBRACKET", "LBRACE", "RBRACE")
    # Delimeters , . ; :
    + ("COMMA", "PERIOD", "SEMI", "COLON")
    # Ellipsis (...)
    + ("ELLIPSIS",)
)
""" ---------------------------------------------------------------------
    |   Regular expression rules for simple tokens
    --------------------------------------------------------------------- 

* Python raw strings are used since they are the most convenient way to write 
regular expression strings

* The name following the t_ must exactly match one of the names supplied in tokens

* The action function can modify the contents of the LexToken object as appropriate.
However, when it is done, the resulting token should be returned. If no value is
returned by the action function, the token is discarded and the next token read.

* Internally, lex.py uses the re module to do its pattern matching. Patterns are 
compiled using the re.VERBOSE flag which can be used to help readability. However, 
be aware that unescaped whitespace is ignored and comments are allowed in this mode. 
If your pattern involves whitespace, make sure you use \s. If you need to match 
the # character, use [#]

* When building the master regular expression, rules are added in the following order:
1.  All tokens defined by functions are added in the same order as they appear in the 
    lexer file.
2.  Tokens defined by strings are added next by sorting them in order of decreasing 
    regular expression length (longer expressions are added first).
    
*
"""
# A string containing ignored characters (spaces and tabs)
t_ignore = " \t"

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

# Increment / Decrement
t_PLUSPLUS = r"\+\+"
t_MINUSMINUS = r"--"

# Structure dereference
t_ARROW = r"->"

# Conditional Operator
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


# Reserved words mappings
reserved_map = {}
for r in reserved:
    reserved_map[
        r.lower()
    ] = r  # Map the reserved word in the reserved tuple from upper case (used as token names) to lower case (used in language).

# Integer literal
t_ICONST = r"\d+([uU]|[lL]|[uU][lL]|[lL][uU])?"

# Floating literal
t_FCONST = r"((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?"

# String literal
t_SCONST = r"\"([^\\\n]|(\\.))*?\""

# Character constant 'c' or L'c'
t_CCONST = r"(L)?\'([^\\\n]|(\\.))*?\'"

""" ---------------------------------------------------------------------
    |   Regular expression rule with some action code
    --------------------------------------------------------------------- """

# Defining a rule so we can track line numbers
def t_NEWLINE(t):
    r"\n+"
    t.lexer.lineno += t.value.count("\n")


# Identifiers
def t_ID(t):
    r"[A-Za-z_][\w_]*"
    # get() returns the value of the key if present. If not, return "ID"
    t.type = reserved_map.get(t.value, "ID")
    if t.type == "ID":
        if len(t.value) > 31:
            print("ERROR: Identifier is longer than 31. Truncating it.")
            t.value = t.value[:31]
    return t


# Comments
def t_comment(t):
    r"/\*(.|\n)*?\*/"
    t.lexer.lineno += t.value.count("\n")


# Comments
def t_illegal_comment(t):
    r"/\*(.|\n)*?"
    print(f"WARNING: Unterminated comment found at line no. {t.lexer.lineno}")
    quit()
    t.lexer.lineno += t.value.count("\n")


def t_illegal_ID(t):
    r"[\d]+[A-Za-z_][\w_]*"
    print(f"ERROR: ID must not begin with a number at line no. {t.lexer.lineno}")


# Single Line Comments
def t_single_line_comment(t):
    r"//.*"
    t.lexer.lineno += t.value.count("\n")


# Preprocessor directive (ignored)
def t_preprocessor(t):
    r"\#(.)*?\n"
    t.lexer.lineno += 1


# Error handling rule for lexer
def t_error(t):
    illegal_char = t.value[0]
    print(f"Illegal character '{illegal_char}'")
    t.lexer.skip(1)