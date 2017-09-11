'''
__author__ = "sgript"


    Expected request format:
    {
    'enquiry': '',               # Boolean, if used all rest parameters are unneeded, module_name can be optionally checked.
    'module_name': '',           # Use this to find applicable methods?
    'id': '',                    # If applicable, i.e. Philips Hue
    'device_type': '',           # Will define fixed categories later.
    'requested_function': '',    # NOTE: See ast module ***
    'parameters': ''
    }

'''
from multiprocessing import Pool


import json
from pubnub.enums import PNStatusCategory
from pubnub.pubnub import PubNub, SubscribeListener
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy

class Client(object):

    def __init__(self, uuid, subscribe_key, publish_key):
        self.pnconfig = PNConfiguration()
        self.pnconfig.uuid = uuid
        self.pnconfig.subscribe_key = subscribe_key
        self.pnconfig.publish_key = publish_key
        self.pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
        self.pnconfig.ssl = True
        self.pnconfig.subscribe_timeout = self.pnconfig.connect_timeout = self.pnconfig.non_subscribe_timeout = 9^99
        self.pubnub = PubNub(self.pnconfig)
        self.my_listener = SubscribeListener()
        self.pubnub.add_listener(self.my_listener)

    def subscribe_channel(self, channel_name, auth_key):
        self.pnconfig.auth_key = auth_key
        self.channel = channel_name

        self.pubnub.subscribe().channels(channel_name).execute()

    def publish_request(self, channel, msg):
        # REVIEW: May need to format py to json

        #msg_json = json.loads(json.dumps(msg))
        msg_json = msg


        self.pubnub.publish().channel(channel).message(msg_json).sync()

        call = self.my_listener.wait_for_message_on(channel)
        result = self.my_listener.wait_for_message_on(channel)

        return(result.message)

    def enquire_modules(self):
        client_.publish_request(self.channel, {"enquiry": True})

    def enquire_module_methods(self, module):
        return(client.publish_request(self.channel, {"enquiry": True, "module_name": module}))

class SmartDevice(object):
    def __init__(self, client):
        self.client = client

    def device_request(self, uuid, enquiry_bool, module_name = None, requested_function = None, parameters = False):
        jsonmsg = {"user_uuid": uuid, "enquiry": enquiry_bool, "module_name": module_name, "requested_function": requested_function, "parameters": parameters}
        return(client.publish_request(client.channel, jsonmsg))

if __name__ == "__main__":
    client = Client('client_test', 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579', 'pub-c-85d5e576-5d92-48b0-af83-b47a7f21739f')
    client.subscribe_channel('NO40ACE6I6', 'V3SIPF92JQ')

    smart = SmartDevice(client)
    result = smart.device_request(client.pnconfig.uuid, False, "philapi", "light_switch", [False, 1])
    print(str(result))
