import requests
import os
import pyimgur
import sys

def take_snapshot():
    """No parameters required"""
    path = '/Users/sgript/Desktop/iotgateway/modules/images/snapshot.jpg'

    f = open(path, 'wb')
    f.write(requests.get('http://admin:aW90bGFiMQ==@192.168.0.27:8080/snapshot.jpg').content)
    f.close()

    CLIENT_ID = "994e3427d60be1d"
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(path, title="Uploaded with PyImgur")
    #os.remove("./images/snapshot.jpg")


    return uploaded_image.link


def guide(func):
    func_to_run = globals()[func]

    return func_to_run.__doc__


    return 0


def get_mac():
    return "00:00:00:00:00:00" # Required but no way to reliably extract, TODO perhaps.
