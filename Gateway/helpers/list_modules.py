import pkgutil
import sys
import os

sys.path.append(".")
import modules

def list_modules(): # ref https://stackoverflow.com/a/1310912
    pkgpath = os.path.dirname(modules.__file__)
    return [module for _, module, _ in pkgutil.iter_modules([pkgpath])]
