# # #
# Just some code to test 'client' behaviour, debug console for PubNub isn't enough.
# # #

import json

import logging
import pubnub
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub, SubscribeListener

pubnub.set_stream_logger('pubnub', logging.DEBUG)
pnconfig = PNConfiguration()

# pnconfig.subscribe_key = 'sub-c-f420fbf8-860e-11e7-9bef-b2d410151acd'
pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
pnconfig.subscribe_key = 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579'
pnconfig.publish_key = 'pub-c-85d5e576-5d92-48b0-af83-b47a7f21739f'
pnconfig.uuid = '332233eeeeeeeo222eee22e3eeeeoooeeeeeeeeeellleeekkkkoowwwwwwwwlllwweeeooo23ookkkko223'
pubnub = PubNub(pnconfig)


my_listener = SubscribeListener()
pubnub.add_listener(my_listener)

pubnub.subscribe().channels(["gateway_auth"]).execute()
my_listener.wait_for_connect()
print('connected')

result = my_listener.wait_for_message_on("gateway_auth")
print(result.message)

pubnub.subscribe().channels(pnconfig.uuid).execute()
result = my_listener.wait_for_message_on(pnconfig.uuid)
print(result.message)

pubnub.unsubscribe_all();

print(type(result.message))
authkey = result.message['auth_key']
channel = result.message['channel']

print(authkey, channel)
pnconfig.auth_key = authkey
pubnub = PubNub(pnconfig)
pubnub.subscribe().channels(channel).execute()
result = my_listener.wait_for_message_on(channel)
print(result.message)
