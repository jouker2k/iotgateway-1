from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub, SubscribeListener

pnconfig = PNConfiguration()

class Client(object):
    def __init__(self, uuid, auth_key, channel, subscribe_key, publish_key):
        pnconfig.auth_key = self.auth_key = auth_key
        pnconfig.uuid = self.uuid = uuid
        pnconfig.subscribe_key = self.subscribe_key = subscribe_key
        pnconfig.publish_key = self.publish_key = publish_key
        pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
        pnconfig.ssl = True
        pnconfig.subscribe_timeout = pnconfig.connect_timeout = pnconfig.non_subscribe_timeout = 9^99

        self.chanenl = channel
        print("Auth key {} initialised".format(self.name))
        print("Secure channel: {}".format(self.channel))

        self.my_listener = SubscribeListener()


        def list_devices(self):



def my_publish_callback(envelope, status):
    if not status.is_error():
        pass
    else:
        pass

# Maybe just make one class for this in a separate file?
class MySubscribeCallback(SubscribeCallback):

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
