'''
__author__ = "@sgript"

'''
import os
import sys
from . import *

def guide(module, func): # provides more info about any module's functions by docstrings
    try:
        i = sys.modules['modules.'+module]
        method = getattr(i, func)

        return {"result": method.__doc__}

    except ModuleNotFoundError:
        return {"module_error": "module could not be found.."}

def get_mac():
    return "0" # Required, but none here.
