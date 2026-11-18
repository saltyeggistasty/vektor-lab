import re
pattern = r"\\sum_(?:\{([^}]+)\}|(\\[a-zA-Z]+|[0-9a-zA-Z]))\^(?:\{([^}]+)\}|(\\[a-zA-Z]+|[0-9a-zA-Z]))\s*(.*?)"
s = r"\sum_{i=0}^{n} i^2"
print("Pattern:", repr(pattern))
print("String:", repr(s))
match = re.search(pattern, s)
print("Match:", match)
if match:
    print("Groups:", match.groups())