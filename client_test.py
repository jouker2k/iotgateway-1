from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()

def init(auth):
    pnconfig.uuid = 'thissACha_31een2991w7pw012'
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
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail
        # Request can be resent using: [status retry];



class MySubscribeCallback(SubscribeCallback):
    def auth(self, auth_info):

        print("auth info: " + str(auth_info))

        authkey = auth_info['auth_key']
        channel = auth_info['channel']

        # Put this into a single method.
        pubnub = init(authkey)

        pubnub.add_listener(MySubscribeCallback())

        pubnub.subscribe().channels(channel).execute()

    def presence(self, pubnub, presence):
        #print(presence.channel)
        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            pass
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.

    def message(self, pubnub, message):
        if message.message == pnconfig.uuid:
            pubnub.subscribe().channels(pnconfig.uuid).execute()
        if 'auth_key' in str(message.message):

            self.auth(message.message)

        print(message.message)
        pass  # Handle new message stored in message.message




# # #
if __name__ == "__main__":
    pubnub = init('')
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels(["gateway_auth"]).execute()

# result = my_listener.wait_for_message_on("gateway_auth")
# print(result.message)

#pubnub.subscribe().channels(pnconfig.uuid).execute()
# result = my_listener.wait_for_message_on(pnconfig.uuid)
# print(result.message)

#pubnub.unsubscribe_all();
# pubnub.remove_listener(my_listener)

# my_listener = SubscribeListener()
# pubnub.add_listener(my_listener)

# print(type(result.message))
# authkey = result.message['auth_key']
# channel = result.message['channel']

# print(authkey, channel)
# pnconfig.auth_key = authkey
# pnconfig.subscribe_key = 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579'
# pubnub = PubNub(pnconfig)
# pubnub.subscribe().channels(channel).execute()
# my_listener.wait_for_connect()
# result = my_listener.wait_for_message_on(channel)
# print('\n\n\n\n\n\n\n\n' + result.message)
