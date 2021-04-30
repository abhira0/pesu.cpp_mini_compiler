import re

text = """ sdfg \nvd vd \ndsfsdf\nfsdfv fsgdsvsd\n
"""

print(len(re.findall(".*(^\n)*.*\n(?m)$", text)))
print(re.findall(".*(^\n)*.*\n(?m)$", text))