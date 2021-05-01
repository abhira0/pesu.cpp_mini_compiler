import re

text = r""" 'Hello  World' """
pattern = r"(\'([^\\\n]|(\\.))*?\')"
print(re.findall(pattern, text)[0][0])