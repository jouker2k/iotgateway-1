from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub, SubscribeListener
import sys

sys.path.append("..")
from helpers import id_generator as idgen

pnconfig = PNConfiguration()
pnconfig.publish_key = 'pub-c-85d5e576-5d92-48b0-af83-b47a7f21739f'
pnconfig.subscribe_key = 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579'
pnconfig.auth_key = 'EMB_48391'
pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
pnconfig.subscribe_timeout = pnconfig.connect_timeout = pnconfig.non_subscribe_timeout = 9^99

pubnub = PubNub(pnconfig)

my_listener = SubscribeListener()
pubnub.add_listener(my_listener)

def LED_on(colour, auth_key = None):
    pnconfig.auth_key = auth_key
    pubnub = PubNub(pnconfig)
    req_id = idgen.id_generator(size = 10)
    pubnub.subscribe().channels('embedded_devices').execute()
    my_listener.wait_for_connect()

    pubnub.publish().channel('embedded_devices').message({"request_id": req_id, "embedded_device": "led", "module": "led", "function": "on", "parameters": [colour]}).sync()
    publish = my_listener.wait_for_message_on('embedded_devices')
    while req_id not in publish.message:
        publish = my_listener.wait_for_message_on('embedded_devices')
        return publish.message

def LED_off(colour, auth_key = None):
    pnconfig.auth_key = auth_key
    pubnub = PubNub(pnconfig)
    req_id = idgen.id_generator(size = 10)
    pubnub.subscribe().channels('embedded_devices').execute()
    my_listener.wait_for_connect()

    pubnub.publish().channel('embedded_devices').message({"request_id": req_id, "embedded_device": "led", "module": "led", "function": "off", "parameters": [colour]}).sync()

    publish = my_listener.wait_for_message_on('embedded_devices')
    while req_id not in publish.message:
        publish = my_listener.wait_for_message_on('embedded_devices')
        return publish.message


def blink(colour, number_of_times, auth_key = None):
    pnconfig.auth_key = auth_key
    pubnub = PubNub(pnconfig)
    req_id = idgen.id_generator(size = 10)
    pubnub.subscribe().channels('embedded_devices').execute()
    my_listener.wait_for_connect()

    pubnub.publish().channel('embedded_devices').message({"request_id": req_id, "embedded_device": "led", "module": "led", "function": "blink", "parameters": [colour, number_of_times]}).sync()

    publish = my_listener.wait_for_message_on('embedded_devices')
    while req_id not in publish.message:
        publish = my_listener.wait_for_message_on('embedded_devices')
        return publish.message

def morse(text, colour, auth_key = None):
    pnconfig.auth_key = auth_key
    pubnub = PubNub(pnconfig)
    req_id = idgen.id_generator(size = 10)

    pubnub.publish().channel('embedded_devices').message({"request_id": req_id, "embedded_device": "led", "module": "morse", "function": "morse_code", "parameters": [text, colour]}).sync()

    publish = my_listener.wait_for_message_on('embedded_devices')
    while req_id not in publish.message:
        publish = my_listener.wait_for_message_on('embedded_devices')
        return publish.message


# blink(["red", 10], "EMB_48391")
# # pubnub.unsubscribe().channels('awesomeChannel').execute()
# # my_listener.wait_for_disconnect()
