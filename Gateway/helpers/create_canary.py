import shutil

def create_canary(file_name):
    try:
        shutil.move("./{}.py".format(file_name), "./modules/{}.py".format(file_name))
    except FileNotFoundError:
        return 1
