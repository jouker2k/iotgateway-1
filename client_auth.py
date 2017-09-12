import hashlib

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()

def init(auth):
    pnconfig.uuid = 'thissACdsssdddididii3eieieidodo--sodsososwososdossosop'
    pnconfig.auth_key = auth
    pnconfig.publish_key = 'pub-c-85d5e576-5d92-48b0-af83-b47a7f21739f'
    pnconfig.subscribe_key = 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579'
    pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
    pnconfig.ssl = True
    pnconfig.subscribe_timeout = 9^99
    pnconfig.connect_timeout = 9^99
    pnconfig.non_subscribe_timeout = 9^99

    pubnub = PubNub(pnconfig)

    return pubnub

def my_publish_callback(envelope, status):
    if not status.is_error():
        print("Client: Message successfully sent to gateway.")
    else:
        print("Client: Error transmitting message to gateway.")


class MySubscribeCallback(SubscribeCallback):
    authed = False
    def __init__(self):
        self.uuid_hash = hashlib.new("sha3_512")
        encode = self.uuid_hash.update((pnconfig.uuid).encode("UTF-8"))

    def auth(self, auth_info):

        print("Auth info: " + str(auth_info))

        # # # Save both of these to file for client for proof-of-concept
        authkey = auth_info['auth_key']
        channel = auth_info['channel']
        # # #

        # We now use our auth key for private channel.
        pubnub = init(authkey)

        pubnub.add_listener(MySubscribeCallback())
        print("Client Connecting to private channel {}..".format(channel))
        pubnub.subscribe().channels(channel).execute()
        self.authed = True

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
        if message.message == self.uuid_hash.hexdigest():
            print("Client: Connecting to UUID channel to retrieve private channel information..")
            pubnub.subscribe().channels(pnconfig.uuid).execute()
        if 'auth_key' in str(message.message) and not self.authed:
            self.auth(message.message)

if __name__ == "__main__":
    pubnub = init('')
    pubnub.add_listener(MySubscribeCallback())
    print("Client: Connecting to gateway to be authenticated..")
    pubnub.subscribe().channels(["gateway_auth"]).execute()
