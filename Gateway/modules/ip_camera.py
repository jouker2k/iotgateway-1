import requests
import os
import pyimgur
import sys

def take_snapshot():
    """No parameters required"""
    path = './modules/images/snapshot.jpg'

    f = open(path, 'wb')
    f.write(requests.get('http://admin:aW90bGFiMQ==@192.168.2.4:8080/snapshot.jpg').content)
    f.close()

    CLIENT_ID = "a244c1881dd54ee"
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(path, title="Uploaded with PyImgur")
    return uploaded_image.link


def get_mac():
    return "0"
