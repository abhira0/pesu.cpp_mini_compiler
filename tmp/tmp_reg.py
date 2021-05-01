import re

try:
    file_code = open("../sourceCode.txt", "r").read()
except:
    file_code = open("./sourceCode.txt", "r").read()

pattern = r"(.*([\\\n]).*)"
print(re.findall(pattern, file_code))
