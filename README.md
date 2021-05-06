# cppminicompiler
 A mini compiler for c++ language (for / switch constructs only)

### Python Lex-yacc
This project is based on PLY (Python Lex - yacc) <br>
See the PLY documentation [here](https://ply.readthedocs.io/en/latest/ "PLY Docs")
## General
Open Windows Terminal (preffered) / cmd / Powershell in `backend` direcory
## Token Rules
* Token Rules are coded in `backend\_0_tokrules.py`
* All the simple regex and regex with action code is written in this file
* No token are generate here
* This file is used by `backend\_1_lexer.py` for generation of tokens
#### Points to note on: Regex
* \[\\\\\n\] -> matches a explicit newline. 
  ```python
  "Hello \n World"
  ```
* \n -or> \(\n\) -or>  \[\\n\] -or> \[\\\\\n\] ->matches a implicit newline
  ```python
  "Hello
  World"
  ```
## Lexer
* Always send raw string to lexer if sent as a string else send a file
* To run lexing phase
  `python _1_lexer.py`
* Input (implicit): The cpp file 
* Output (implicit): 
  * stdout: LexTokens
  * `p1_symbol_table.json` -> with ASCII and number conversion
  * `p2_symbol_table.json` -> without ASCII and number conversion
## Parser
* Synatx Analysis and Semantic Analysis is done here
* To make it happen, run the following:
  * `python _2_parser.py`
* Input (implicit): `p2_symbol_table.json`
* Output (implicit): 
  * stdout: 
    * Three Address Code
    * Scope tables
    * Symbol table
    * Abstarct syntax tree
  * `3code.txt` -> Three Address Code
  * `symbol_table.pkl` -> SymbolTable class is propogated from parser to optimizer
  * ply op: `parset.out` and `parsetab.py`
## Optimizer
* Optimization
* To make it happen, run the following:
  * `python _3_optimizer.py`
* Input (implicit): 
  * `symbol_table.pkl`
  * `3code.txt`
* Output (implicit): 
  * stdout: 
    * Optimized Three Address Code
    * Updated Symbol table
  * `optimized-3code` -> Optimized Three Address Code
