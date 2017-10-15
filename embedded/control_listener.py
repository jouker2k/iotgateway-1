from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub

from led import led, morse
import db
import sys, json

import unicodedata


def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];


class Embedded_Devices(SubscribeCallback):

    def __init__(self):
        password = raw_input("Database password: ")
        host = 'ephesus.cs.cf.ac.uk'
        user = 'c1312433'
        database = 'c1312433'
        self.db = db.DB(host, user, password, database)

        pnconfig = PNConfiguration()

        pnconfig.subscribe_key = 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579'
        pnconfig.publish_key = 'pub-c-85d5e576-5d92-48b0-af83-b47a7f21739f'
        pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
        pnconfig.subscribe_timeout = pnconfig.connect_timeout = pnconfig.non_subscribe_timeout = 9^99
        pnconfig.auth_key = self.db.embedded_devices_key()
        self.pubnub = PubNub(pnconfig)

        self.pubnub.add_listener(self)
        self.pubnub.subscribe().channels('embedded_devices').execute()

    def publish_request(self, channel, msg):
        msg_json = json.loads(json.dumps(msg))
        self.pubnub.publish().channel(channel).message(msg_json).async(my_publish_callback)

    def presence(self, pubnub, presence):
        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            print("UnexpectedDisconnect")
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            print("Connected")
            pass
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            print("Reconnected")
            pass
    def message(self, pubnub, message):
        msg = message.message
        # // {"request_id": "welelqee", "embedded_device": "led", "module": "morse", "function": "morse_code", "parameters": ["test", "yellow"]}
        if "device_response" not in msg.keys():
            parameters = msg['parameters']
            try:
                module = sys.modules['led.' + msg['module']]
                method_to_call = getattr(module, msg['function'])
                try:
                    parameters = list(unicodedata.normalize('NFKD', msg['parameters']).encode('ascii','ignore'))
                except:
                    pass

                result = method_to_call(*parameters)

                self.publish_request(message.channel, {"device_response": {"success": result, "request_id": msg["request_id"]}})
                print("\nSuccessful request: {}".format(msg))

            except KeyError as e:
                print("Error occured: Value does not exist in the message: {}\nOn request: {}".format(e, msg))

            except Exception as e:
                print("\nError occured: {}\nOn request: {}".format(e, msg))


if __name__ == "__main__":
    emb = Embedded_Devices()
