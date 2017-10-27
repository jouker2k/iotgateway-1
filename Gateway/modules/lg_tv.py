import sys
import json
import logging

sys.path.append("..")
from helpers.pylgtv_master.pylgtv import WebOsClient
from helpers.python_lgtv_master.lg import Remote

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

## See README.md for more info and Gateway/helpers/
## https://github.com/grieve/python-lgtv for finding tv
## https://github.com/TheRealLink/pylgtv for rest
## see /helpers/ for license and full details
## Calls the wrapper cleanly, acting as the module face to user-applications.


class TV(object):
    def __init__(self):
        self.webos_client = None

    def find_app_from_apps(self, app):
        apps = get_apps()

        # some names of apps are not straight forward so this will find them
        index_app = next(index for (index, d) in enumerate(apps) if app in d["id"])

        return apps[index_app]["id"]

    def connect(self):
        try:
            self.webos_client = WebOsClient(Remote.find_tvs(first_only=True))
        except:
            return json.dumps({"lg_err": "tv not connected"})


tv = TV()
def get_volume():
    conn = tv.connect()
    if conn is not None:
        return conn

    return tv.webos_client.get_volume()

def set_volume(volume):
    conn = tv.connect()
    if conn is not None:
        return conn

    tv.webos_client.set_volume(volume)
    return json.dumps({"volume": volume})


def volume_up():
    conn = tv.connect()
    if conn is not None:
        return conn

    tv.webos_client.volume_up()
    return json.dumps({"volume_up": "done"})


def volume_down():
    conn = tv.connect()
    if conn is not None:
        return conn

    tv.webos_client.volume_down()
    return json.dumps({"volume_down": "done"})

def open_url(url):
    conn = tv.connect()
    if conn is not None:
        return conn

    try:
        tv.webos_client.open_url(url)
        return json.dumps({"opened_url": url})

    except:
        return json.dumps({"lg_err": "issue launching app"})

def launch_app(app):
    conn = tv.connect()
    if conn is not None:
        return conn

    try:
        app = tv.find_app_from_apps(app)
        tv.webos_client.launch_app(app)
        return json.dumps({"launched_app": app})

    except:
        return json.dumps({"lg_err": "issue launching app"})

def launch_app_with_params(app, param):
    conn = tv.connect()
    if conn is not None:
        return conn

    try:
        app = tv.find_app_from_apps(app)
        tv.webos_client.launch_app_with_params(app, param)
        return json.dumps({"launched_app": app, "param": param})

    except:
        return json.dumps({"lg_err": "issue launching app with param"})

def get_apps():
    conn = tv.connect()
    if conn is not None:
        return conn

    return tv.webos_client.get_apps()

def current_app():
    conn = tv.connect()
    if conn is not None:
        return conn

    return tv.webos_client.get_current_app()

def get_services():
    conn = tv.connect()
    if conn is not None:
        return conn

    return tv.webos_client.get_services()

def get_inputs():
    conn = tv.connect()
    if conn is not None:
        return conn

    return tv.webos_client.get_inputs()

def set_input(input):
    conn = tv.connect()
    if conn is not None:
        return conn

    return tv.webos_client.set_input(input)

def get_audio_status(self):
    conn = tv.connect()
    if conn is not None:
        return conn

    return tv.webos_client.get_audio_status()

def get_muted():
    conn = tv.connect()
    if conn is not None:
        return conn

    return tv.webos_client.get_muted()

def set_mute(mute):
    conn = tv.connect()
    if conn is not None:
        return conn

    return tv.webos_client.set_mute(mute)

def power_on():
    conn = tv.connect()
    if conn is not None:
        return conn

    tv.webos_client.power_on()
    return json.dumps({"power_on": "done"})


def power_off():
    conn = tv.connect()
    if conn is not None:
        return conn

    tv.webos_client.power_off()
    return json.dumps({"power_off": "done"})


def switch_3d_on():
    conn = tv.connect()
    if conn is not None:
        return conn

    tv.webos_client.turn_3d_on()
    return json.dumps({"3d_on": "done"})

def switch_3d_off():
    conn = tv.connect()
    if conn is not None:
        return conn

    tv.webos_client.turn_3d_off()
    return json.dumps({"3d_off": "done"})

def send_message(message):
    conn = tv.connect()
    if conn is not None:
        return conn

    tv.webos_client.send_message(message)
    return json.dumps({"send_message": "done"})
