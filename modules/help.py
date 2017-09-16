import os
import sys

def guide(module, func):
    try:
        i = __import__(module)
        method = getattr(i, func)

        return {"result": method.__doc__}

    except ModuleNotFoundError:
        return {"error": "module could not be found.."}

def get_mac():
    return 0
