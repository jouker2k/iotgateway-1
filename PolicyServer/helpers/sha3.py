'''
__author__ = "@sgript"

'''
import hashlib

def sha3(x):
    shahash = hashlib.new("sha3_512")
    encode = shahash.update((x).encode("UTF-8"))
    return shahash.hexdigest()
