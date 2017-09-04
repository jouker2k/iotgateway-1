# # # Authentication code for clients connecting to gateway via pubnub

# TODO: However, first somehow check how many people are on the channel?
# TODO: Enable Access Manager again, perhaps do a READ-ONLY gateway_auth channel -- so no messages sent here_now
# TODO: Maybe need a way to destroy channel after a leave event or a timeout event (UUID channel no longer in use..)?
# TODO: Implement some channel for global announcements to all devices
# .
# .
# TODO: Clean up code.

# # #

import string
import random
import json

import logging
import pubnub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub

pubnub.set_stream_logger('pubnub', logging.DEBUG)
pnconfig = PNConfiguration()

# Keys - Perhaps move somewhere remote
pnconfig.subscribe_key = 'sub-c-f420fbf8-860e-11e7-9bef-b2d410151acd'
pnconfig.publish_key = 'pub-c-06728f1a-f12a-45b9-a501-70e1beeb88d1'
pnconfig.secret_key = 'sec-c-MmVjMzllOTQtNGQyMC00M2M5LWE5OGMtOWU2YTM3Mzk1MmQ3'
pnconfig.ssl = True
pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
pnconfig.uuid = 'gateway'

pubnub = PubNub(pnconfig)

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def my_publish_callback(envelope, status): # More info on publish callback -> https://www.pubnub.com/docs/python/pubnub-python-sdk
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue

class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):

        if presence.channel == "gateway_auth":
            authkey = id_generator() # This is used for the randomly generated auth key

            envelope = pubnub.here_now().channels(presence.uuid).include_uuids(True).include_state(True).sync()

            # TODO
            print("\n\n\n\n------------------UUIDs present-------------------------")
            users = envelope.result.channels[0].occupants
            for occupant in users:
                print(occupant.uuid) # - lists all uuids in channel, if more than one can later 'blacklist' ones not meant to be in the channel -> "do not serve, suspicious"
            print("Occupancy of channel:" + str(envelope.result.total_occupancy)) # gets number of users in the channel - safety check
            print("----------------------------------------------------------------\n\n\n")

            # pubnub.grant().channels(Update[presence.uuid]).auth_keys(authkey).read(True).write(True).sync() # TODO

            # Add channel to group, making it easier to access/list later.
            pubnub.add_channel_to_channel_group().channels(
                presence.uuid).channel_group("comm_channels").sync()

            pubnub.publish().channel(presence.uuid).message(
                {"auth_key": authkey, "sub_key": pnconfig.subscribe_key, "pub_key": pnconfig.publish_key}).async(my_publish_callback) # Send data over 1-1 channel
        else:
            pubnub.publish().channel(presence.uuid).message(
                {"error": "Too many occupants in channel, regenerate UUID."}).async(my_publish_callback) # + Maybe something later to blacklist suspicious UUIDs/devices.
            pubnub.remove_channel_from_channel_group().channels(
                presence.uuid).channel_group("comm_channel").sync() # Remove, as the channel is not trustworthy.

    def status(self, pubnub, status): # More info on categories -> https://www.pubnub.com/docs/python/pubnub-python-sdk
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass

        elif status.category == PNStatusCategory.PNConnectedCategory:
            pass

        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass

        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass

    def message(self, pubnub, message):
        pass  # Handle new message stored in message.message

# Add listener to auth channel
listener = MySubscribeCallback()


pubnub.add_listener(listener)

pubnub.grant().channels(["gateway_auth"]).auth_keys(
    "auth").read(True).write(True).sync()

pubnub.subscribe().channels("gateway_auth").with_presence().execute()
pubnub.subscribe().channel_groups("comm_channels").with_presence().execute()
