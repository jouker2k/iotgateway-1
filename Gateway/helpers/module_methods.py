import ast
import sys

# adapted from ref https://stackoverflow.com/a/31005891

def top_level_functions(body):
    return (f for f in body if isinstance(f, ast.FunctionDef))

def parse_ast(filename):
    try:
        with open("./modules/"+filename, "rt") as file:
            return ast.parse(file.read(), filename=filename)
    except IOError as exc:
        raise IOError("%s" % (exc.strerror))

def find(module):
    if module[-3:] != '.py':
        module = module + '.py'
    tree = parse_ast(module)

    functions = []
    for func in top_level_functions(tree.body):
        functions.append(func.name)

    return functions
