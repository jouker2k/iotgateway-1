import string
import random

def id_generator(size=10, chars=string.ascii_uppercase + string.digits): # https://stackoverflow.com/a/2257449
    return ''.join(random.choice(chars) for _ in range(size))
