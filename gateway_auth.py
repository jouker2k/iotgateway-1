# Authentication code for pubnub

# TODO: Send Auth data back over UUID channel
# TODO: However, first somehow check how many people are on the channel?
# TODO: Enable Access Manager again, perhaps do a READ-ONLY gateway_auth channel -- so no messages sent here_now
# TODO: Preceeding messages after authentication must be on UUID channels, so we know any messages are from established UUID channels and need replies.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import logging
import pubnub

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub

pubnub.set_stream_logger('pubnub', logging.DEBUG)
pnconfig = PNConfiguration()

# Keys - Perhaps move over to a completely inaccessible server except for this IoT Gateway
pnconfig.subscribe_key = 'sub-c-f420fbf8-860e-11e7-9bef-b2d410151acd'
pnconfig.publish_key = 'pub-c-06728f1a-f12a-45b9-a501-70e1beeb88d1'
pnconfig.secret_key = 'sec-c-MmVjMzllOTQtNGQyMC00M2M5LWE5OGMtOWU2YTM3Mzk1MmQ3'
#pnconfig.auth_key = 'auth'
pnconfig.ssl = True
pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR

pubnub = PubNub(pnconfig)

# TODO: Handling incoming data properly - Create new channels for UUIDs

def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        print(envelope.message)
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];


class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):

        print(presence.uuid) # capture newly joined user's uuid so can make a new subscription channel to listen on.

        pubnub.subscribe().channels(presence.uuid).with_presence().execute()

        # TODO: Pass the auth key I'll make here
        pubnub.publish().channel(presence.uuid).message("Hello!!").async(my_publish_callback)

        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            #pubnub.publish().channel("gateway_auth").message("hello!!").async(my_publish_callback)
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
        pass  # Handle new message stored in message.message


# REVIEW: Eventually do something with this.. Remove or whatever.
#def here_now_callback(result, status):
#     if status.is_error():
#         # handle error
#         return
#
#     for channel_data in result.channels:
#         print("---")
#         print("channel: %s" % channel_data.channel_name)
#         print("occupancy: %s" % channel_data.occupancy)
#
#         print("occupants: %s" % channel_data.channel_name)
#     for occupant in channel_data.occupants:
#         print("uuid: %s, state: %s" % (occupant.uuid, occupant.state))
#
# pubnub.here_now()\
#     .channels("gateway_auth")\
#     .include_uuids(True)\
#     .async(here_now_callback)

# Add listener to auth channel
listener = MySubscribeCallback()
pubnub.add_listener(listener)

pubnub.grant().channels(["gateway_auth"]).auth_keys("auth").read(True).write(True).sync()

pubnub.subscribe().channels("gateway_auth").with_presence().execute()
result = listener.wait_for_message_on('gateway_auth')
print(result.message)
