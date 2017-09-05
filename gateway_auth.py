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
        print("\n\n\n\n\n\n\n\n\n\nUUID IS: " + presence.uuid)

        if presence.channel == "gateway_auth": # Only do this when someone joins the gateway_auth channel.
            authkey = id_generator() # This is used for the randomly generated auth key

            print("\n\n\n\n\n\n\n\n\nOK IN HERE\n\n\n\n\n\n")

            pubnub.grant().channels(presence.uuid).read(True).write(True).sync()
            pubnub.subscribe().channels(presence.uuid).with_presence().execute()
            envelope = pubnub.here_now().channels(presence.uuid).include_uuids(True).include_state(True).sync()
            pubnub.publish().channel('gateway_auth').message('OK?').async(my_publish_callback)
            users_in_channel = envelope.result.total_occupancy

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

            elif users_in_channel < 1:
                print("Internal error: no users in the UUID channel: {}".format(presence.uuid))
                pass

            else: # We can send the keys now

                # Add channel to group, making it easier to access/list later.
                pubnub.add_channel_to_channel_group().channels(
                    presence.uuid).channel_group("comm_channels").sync()

                # Only need to send auth key (because permissions will change) and pub key (as they will only be supplied to subscribe key to begin with)
                pubnub.publish().channel(presence.uuid).message(
                    {"auth_key": authkey, "pub_key": pnconfig.publish_key}).async(my_publish_callback) # Send data over 1-1 channel

                print("\n\n\n\nAUTHING {}".format(presence.uuid))
                #pubnub.grant().channels(presence.uuid).read(False).write(False).sync()

                print("\n\n\n\nAUTHING {}".format(presence.uuid))
                #pubnub.grant().channels(presence.uuid).auth_keys(authkey).read(True).write(True).sync()

                 # TODO

        elif presence.channel != "gateway_auth":
            pubnub.publish().channel(presence.uuid).message({"auth_key": 'lol', "pub_key": pnconfig.publish_key}).async(my_publish_callback)

            pubnub.grant().channels(presence.uuid).read(False).write(False).sync()
            pubnub.grant().channels(presence.uuid).auth_keys('lol').read(True).write(True).sync()

            time.sleep(10)
            pubnub.publish().channel(presence.uuid).message('hello?').async(my_publish_callback)

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

pubnub.grant().read(True).write(True).sync()
pubnub.grant().channels(["gateway_auth"]).read(True).write(False).sync()
#pubnub.grant().channel_groups("comm_channels").read(True).write(False).sync()

pubnub.subscribe().channels("gateway_auth").with_presence().execute()
pubnub.subscribe().channel_groups("comm_channels").with_presence().execute()
