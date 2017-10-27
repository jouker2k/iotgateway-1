'''
__author__ = "@sgript"

Makeshift client for testcases + videos recorded.
'''

import json
import time
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub, SubscribeListener

pnconfig = PNConfiguration()
pnconfig.uuid = 'speedtestClient'

pnconfig.publish_key = 'pub-c-85d5e576-5d92-48b0-af83-b47a7f21739f'
pnconfig.subscribe_key = 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579'
pnconfig.auth_key = 'V575MH48KA'
# pnconfig.auth_key = '0F2D18PV1CTA4JIM98MX9FTZ87Q9IZ4FW53LRHXT3R' # admin key
pnconfig.ssl = True
pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
pnconfig.subscribe_timeout = pnconfig.connect_timeout = pnconfig.non_subscribe_timeout = 9^99

pubnub = PubNub(pnconfig)

pubnub = PubNub(pnconfig)
my_listener = SubscribeListener()
pubnub.add_listener(my_listener)
pubnub.subscribe().channels('SECURE.BN9NDS0PFC').execute()
my_listener.wait_for_connect()
print("Test #18")

msg = json.loads(json.dumps({"enquiry": False, "module_name": "philapi", "requested_function": "light_switch", "parameters": [True, 1]}))

accumulated_time = 0
for x in range(0,1):
    start = time.time()
    pubnub.publish().channel('SECURE.BN9NDS0PFC').message(msg).sync()
    test1 = my_listener.wait_for_message_on('SECURE.BN9NDS0PFC')
    print("My request: " + str(msg))
    # print("Request serialised: " + str(test1.message))
    test2 = my_listener.wait_for_message_on('SECURE.BN9NDS0PFC')
    # print(x + 1)
    print("Gateway response: " + str(test2.message))
    end = time.time()

    loop_average = end - start
    accumulated_time += loop_average

# print("accumulated: " + str(accumulated_time))
