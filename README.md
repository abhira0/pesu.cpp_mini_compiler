# cppminicompiler
 A mini compiler for c++ language (for / switch constructs only)

### Python Lex-yacc
This project is based on PLY (Python Lex - yacc) <br>
See the PLY documentation [here](https://ply.readthedocs.io/en/latest/ "PLY Docs")

## Lexer
* Always send raw string to lexer if sent as a string else send a file
* To run lexing phase
  * To generate output file: `python backend\_1_lexer.py > _1_lex_op.txt`
  * To get stdout on terminal: `python backend\_1_lexer.py`

### Regex
* \n -> matches a implicit newline. 
```python
"Hello \n World"
```
* \\\\\n -> matched a explicit newline
```python
"Hello
World"
```
