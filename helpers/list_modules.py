import pkgutil
import sys
import os
#from .. import modules
sys.path.append(".")
import modules

def list_modules():
    pkgpath = os.path.dirname(modules.__file__)
    return [module for _, module, _ in pkgutil.iter_modules([pkgpath])]
  # https://stackoverflow.com/a/1310912
