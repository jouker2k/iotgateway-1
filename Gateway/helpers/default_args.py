import inspect

def get_default_args(func): # ref https://stackoverflow.com/a/12627202
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }
