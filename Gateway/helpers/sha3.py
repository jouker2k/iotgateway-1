import hashlib

def hash(x):
    shahash = hashlib.new("sha3_512")
    encode = shahash.update((x).encode("UTF-8"))
    return shahash.hexdigest()
