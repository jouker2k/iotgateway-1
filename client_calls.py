'''
__author__ = "sgript"
'''

import json

from pubnub.enums import PNStatusCategory
from pubnub.callbacks import SubscribeCallback
from pubnub.pubnub import PubNub, SubscribeListener
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy

class Client(SubscribeCallback):

    def __init__(self, uuid, subscribe_key, publish_key):
        self.pnconfig = PNConfiguration()
        self.pnconfig.uuid = uuid
        self.pnconfig.subscribe_key = subscribe_key
        self.pnconfig.publish_key = publish_key
        self.pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
        self.pnconfig.ssl = True
        self.pnconfig.subscribe_timeout = self.pnconfig.connect_timeout = self.pnconfig.non_subscribe_timeout = 9^99
        self.pubnub = PubNub(self.pnconfig)

    def subscribe_channel(self, channel_name, auth_key):
        self.pnconfig.auth_key = auth_key
        self.channel = channel_name
        self.pubnub = PubNub(self.pnconfig)
        self.pubnub.add_listener(self) # Adding the listener as itself as it contains the SubscribeCallback object.

        self.pubnub.subscribe().channels(channel_name).execute()

    def publish_request(self, channel, msg):
        # REVIEW: May need to format py to json
        msg_json = json.loads(json.dumps(msg))
        self.pubnub.publish().channel(channel).message(msg_json).async(my_publish_callback)

    def presence(self, pubnub, presence):
        #print(presence.channel)
        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            pass

        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass

        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass

    def message(self, pubnub, message):
        print(message.message)
        pass

def my_publish_callback(envelope, status):
    if not status.is_error():
        print("message success")
        pass
    else:
        print("message error")
        pass


if __name__ == "__main__":
    client = Client('client_test', 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579', 'pub-c-85d5e576-5d92-48b0-af83-b47a7f21739f')
    client.subscribe_channel('I50ANAY3F6', '3ZABY058UU')

    client.publish_request('I50ANAY3F6', {"enquiry": True, "module_name": "philapi"})
