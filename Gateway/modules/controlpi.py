from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub, SubscribeListener
import sys

pnconfig = PNConfiguration()
pnconfig.publish_key = 'pub-c-85d5e576-5d92-48b0-af83-b47a7f21739f'
pnconfig.subscribe_key = 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579'
pnconfig.auth_key = 'EMB_48391'
pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
pnconfig.subscribe_timeout = pnconfig.connect_timeout = pnconfig.non_subscribe_timeout = 9^99

pubnub = PubNub(pnconfig)

my_listener = SubscribeListener()
pubnub.add_listener(my_listener)
pubnub.subscribe().channels('embedded_devices').execute()
my_listener.wait_for_connect()

def LED_on(auth_key = None):
    pnconfig.auth_key = auth_key
    pubnub = PubNub(pnconfig)

    pubnub.publish().channel('embedded_devices').message({"command": {"pi": {"led": 1}}}).sync()

    publish = my_listener.wait_for_message_on('embedded_devices')
    while "command" in publish.message:
        publish = my_listener.wait_for_message_on('embedded_devices')
        print(publish.message)

def LED_off(auth_key = None):
    pnconfig.auth_key = auth_key
    pubnub = PubNub(pnconfig)

    pubnub.publish().channel('embedded_devices').message({"command": {"pi": {"led": 0}}}).sync()

    publish = my_listener.wait_for_message_on('embedded_devices')
    while "command" in publish.message:
        publish = my_listener.wait_for_message_on('embedded_devices')
        print(publish.message)

def LED_state(auth_key = None):
    pnconfig.auth_key = auth_key
    pubnub = PubNub(pnconfig)

    pubnub.publish().channel('embedded_devices').message({"command": {"pi": {"led": -1}}}).sync()

    publish = my_listener.wait_for_message_on('embedded_devices')
    while "command" in publish.message:
        publish = my_listener.wait_for_message_on('embedded_devices')
        print(publish.message)


# # LED_on('EMB_48391')
# # pubnub.unsubscribe().channels('awesomeChannel').execute()
# # my_listener.wait_for_disconnect()
