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
import time

import logging
import pubnub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub

pubnub.set_stream_logger('pubnub', logging.DEBUG)
pnconfig = PNConfiguration()

# Keys - Perhaps move somewhere remote
# pnconfig.subscribe_key = 'sub-c-f420fbf8-860e-11e7-9bef-b2d410151acd'
# pnconfig.publish_key = 'pub-c-06728f1a-f12a-45b9-a501-70e1beeb88d1'
# pnconfig.secret_key = 'sec-c-MmVjMzllOTQtNGQyMC00M2M5LWE5OGMtOWU2YTM3Mzk1MmQ3'
pnconfig.subscribe_key = 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579'
pnconfig.publish_key = 'pub-c-85d5e576-5d92-48b0-af83-b47a7f21739f'
pnconfig.secret_key = 'sec-c-YmZlMzkyYTctZDg1NC00ZTY0LWE3YzctNTkzOGRjZjk0OTI5'
pnconfig.subscribe_timeout = 9^99
pnconfig.connect_timeout = 9^99
pnconfig.non_subscribe_timeout = 9^99
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
            print("\n\n\nUUID: {}\n\n\n".format(presence.uuid))

            pubnub.grant().channels(presence.uuid).read(True).write(True).sync()
            pubnub.subscribe().channels(presence.uuid).with_presence().execute()

            pubnub.publish().channel('gateway_auth').message(presence.uuid).async(my_publish_callback)

            # Check UUID channel info
            envelope = pubnub.here_now().channels(presence.uuid).include_uuids(True).include_state(True).sync()
            users_in_channel = envelope.result.total_occupancy

            # Someone could be spying
            if users_in_channel > 1:
                uuids_in_channel = []
                users = envelope.result.channels[0].occupants

                for occupant in users: # If there is indeed multiple people in the channel only then we bother to check who.
                    print(occupant.uuid) # - lists all uuids in channel, if more than one can later 'blacklist' ones not meant to be in the channel -> "do not serve, suspicious"
                    uuids_in_channel.append(occupant.uuid)

                if presence.uuid in uuids_in_channel:
                    uuids_in_channel.remove(presence.uuid)

                    # TODO: Save somewhere locally the suspicious UUID to read back in later - Need condition at the top to check then if this is the UUID of the user trying to auth to deny them.

                pubnub.publish().channel(presence.uuid).message(
                    {"error": "Too many occupants in channel, regenerate UUID."}).async(my_publish_callback) #

            # Nothing to do here.
            elif users_in_channel < 1:
                print("\n\nInternal error: no users in the UUID channel: {}".format(presence.uuid))
                pass

        elif presence.channel != "gateway_auth" and presence.uuid == presence.channel:
            print('\n\n\nOK USER IS IN UUID CHANNEL\n\n\n')
            authkey = id_generator()
            channelName = id_generator()

            # Add channel to group, making it easier to access/list later.
            # pubnub.add_channel_to_channel_group().channels(
            #     presence.uuid).channel_group("comm_channels").sync()

            # Only need to send auth key (because permissions will change) and pub key (as they will only be supplied to subscribe key to begin with)
            pubnub.publish().channel(presence.uuid).message(
                {"channel": channelName, "auth_key": authkey, "pub_key": pnconfig.publish_key}).async(my_publish_callback) # Send data over 1-1 channel

            pubnub.unsubscribe().channels(presence.uuid).execute()
            #pubnub.grant().channels(channelName).read(False).write(False).manage(True).sync()
            pubnub.grant().channels(channelName).auth_keys(authkey).read(True).write(True).manage(True).sync()
            # pnconfig.auth_key = authkey
            # pubnub = PubNub(pnconfig)
            pubnub.subscribe().channels(channelName).execute()

        elif presence.channel != "gateway_auth" and presence.uuid != presence.channel:
            #msg = "This is the {} channel".format(presence.channel)
            #pubnub.publish().channel(presence.channel).message(msg).async(my_publish_callback)
            pass

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

if __name__ == "__main__":
    listener = MySubscribeCallback()
    pubnub.add_listener(listener)

    pubnub.grant().channels(["gateway_auth"]).read(True).write(True).manage(True).sync()
    pubnub.subscribe().channels(["gateway_auth"]).with_presence().execute()

# pnconfig.auth_key = 'UJARR4SCD1'
# pubnub = PubNub(pnconfig)
# pubnub.subscribe().channels(["E0BXKLR4T9"]).with_presence().execute()
