# # #
# Just some code to test 'client' behaviour, debug console for PubNub isn't enough.
# # #

from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener

pnconfig = PNConfiguration()

pnconfig.subscribe_key = 'sub-c-f420fbf8-860e-11e7-9bef-b2d410151acd'
pnconfig.publish_key = 'pub-c-06728f1a-f12a-45b9-a501-70e1beeb88d1'
pnconfig.uuid = 'test_client3'

pubnub = PubNub(pnconfig)

my_listener = SubscribeListener()
pubnub.add_listener(my_listener)

pubnub.subscribe().channels([pnconfig.uuid, 'gateway_auth']).execute()
my_listener.wait_for_connect()
print('connected')

#pubnub.publish().channel('awesomeChannel').message({'fieldA': 'awesome', 'fieldB': 10}).sync()
result = my_listener.wait_for_message_on(pnconfig.uuid)
print(result.message)

# pubnub.unsubscribe().channels('awesomeChannel').execute()
# my_listener.wait_for_disconnect()
# print('unsubscribed')
