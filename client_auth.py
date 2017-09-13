import hashlib

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub


def my_publish_callback(envelope, status):
    if not status.is_error():
        print("Client: Message successfully sent to gateway.")
    else:
        print("Client: Error transmitting message to gateway.")

class Client(SubscribeCallback):
    authed = False
    def __init__(self, uuid):
        self.pnconfig = PNConfiguration()
        self.pnconfig.uuid = uuid
        self.pnconfig.publish_key = 'pub-c-85d5e576-5d92-48b0-af83-b47a7f21739f'
        self.pnconfig.subscribe_key = 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579'
        self.pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
        self.pnconfig.ssl = True
        self.pnconfig.subscribe_timeout = 9^99
        self.pnconfig.connect_timeout = 9^99
        self.pnconfig.non_subscribe_timeout = 9^99

        self.pubnub = PubNub(self.pnconfig)
        self.pubnub.add_listener(self)

        print("Client: Connecting to gateway to be authenticated..")
        self.pubnub.subscribe().channels(["gateway_auth"]).execute()

        self.uuid_hash = hashlib.new("sha3_512")
        encode = self.uuid_hash.update((self.pnconfig.uuid).encode("UTF-8"))

    def presence(self, pubnub, presence):
        pass  # Nothing to do for client.

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            print("Client: Unexpectedly disconnected.")

        elif status.category == PNStatusCategory.PNConnectedCategory:
            print("Client: Connected.")

        elif status.category == PNStatusCategory.PNReconnectedCategory:
            print("Client: Reconnected.")

    def message(self, pubnub, message):
        print(message.message)
        uuid_hash = hashlib.new("sha3_512")
        encode = uuid_hash.update((self.pnconfig.uuid).encode("UTF-8"))
        print("hash digest is: " + uuid_hash.hexdigest())
        if message.message == uuid_hash.hexdigest():
            print("Client: Connecting to UUID channel to retrieve private channel information..")
            pubnub.subscribe().channels(self.pnconfig.uuid).execute()

        if 'auth_key' in message.message and not self.authed:
            # TODO Integrate client calls into here as well - So drop subscription of old channel and subscribe to new one.
            self.pubnub.unsubscribe().channels(self.pnconfig.uuid).execute();

            authkey = message.message['auth_key']
            channel = message.message['channel']

            self.pnconfig.auth_key = authkey
            print("Client Connecting to private channel {}..".format(message.channel))
            self.pubnub.subscribe().channels(message.channel).execute()
            self.authed = True

            testing = input("this is a test: ")
            print(testing)


            pass

if __name__ == "__main__":
    client = Client("65628823891u2991913579199kkkkkk")
