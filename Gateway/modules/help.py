import os
import sys
from . import *

def guide(module, func):
    try:
        i = sys.modules['modules.'+module]
        method = getattr(i, func)

        return {"result": method.__doc__}

    except ModuleNotFoundError:
        return {"module_error": "module could not be found.."}

def get_mac():
    return "00:00:00:00:00:00" # Required, but none here.
