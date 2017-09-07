from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from modules import *

import requests
import json

pnconfig = PNConfiguration()

pnconfig.subscribe_key = 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579'
pnconfig.publish_key = 'pub-c-85d5e576-5d92-48b0-af83-b47a7f21739f'
pnconfig.uuid = '012345'
pnconfig.auth_key = 'sgriptkey'
pnconfig.secret_key = 'sec-c-YmZlMzkyYTctZDg1NC00ZTY0LWE3YzctNTkzOGRjZjk0OTI5'

pubnub = PubNub(pnconfig)

# TODO: HANDLE RESPONSES TO GIVE TO CLIENT (ERROR CODES)
# TODO: For Philips API calls do better error returns, such as passing on those returned via the API.

class ButtonNotPressed(Exception):
    pass



def bridge_ip():
    list_bridges = requests.get('https://www.meethue.com/api/nupnp')
    bridge_ip = json.loads(list_bridges.text) # string to json
    if len(bridge_ip) > 1:
        # TODO: Selection screen maybe here, if multiple IPs (multiple bridges) detected..
        pass
    else:
        bridge_ip = bridge_ip[0]['internalipaddress'] # if just one bridge, take its ip

    return bridge_ip

def bridge_auth():
    api_url = 'http://{}/api'.format(bridge_ip())
    bridge_name = input('Name your Philips Bridge you wish to add: ')
    print("Great! You've named this bridge " + bridge_name)

    # get api id
    result = ''
    while True:
        try:
            press_auth = input('Enter Y once you have pressed the button on the Hue Bridge: ')
            if press_auth != 'Y':
                raise ButtonNotPressed
            else:
                # once button has been pressed, we can make a successful request.
                data = json.dumps({"devicetype":"my_hue_app#"+bridge_name})
                result = json.loads(requests.post(api_url, data).text)[0]

                if 'error' in result:
                    raise ButtonNotPressed
                else:
                    print('The key found is: ' + result['success']['username'])
                    result = result['success']['username']
                    break

        except ButtonNotPressed as e:
            print('There was an error, please try press the button again.')
            continue

    return result

def show_hues(bridge_key):
    # TODO: REPLACE HARDCODED AUTH KEY WITH RETRIEVED ONE --> bridge_auth()
    req = requests.get('http://{0}/api/{1}/lights'.format(bridge_ip(), bridge_key))

    # like in bridge_auth_key func will need to dump the json using dumps() then use loads()
    bulbs = json.loads(req.text)
    print(bulbs)
    bulbs_available = []
    for bulb_id in bulbs:
        print("Bulb ID: " + bulb_id + " (Name: {})".format(bulbs[bulb_id]['name'])) # perhaps make this into a JSON instead for client's convenience

    print(', '.join(map(str, bulbs_available)))

def light_switch(state, bridge_key, bulb_id):
    api_url = 'http://{0}/api/{1}/lights/{2}/state'.format(bridge_ip(), bridge_key, bulb_id)

    data = json.dumps({"on":state})
    req = requests.put(api_url, data)

    print(req.text)


def light_brightness(brightness, bridge_key, bulb_id):
    api_url = 'http://{0}/api/{1}/lights/{2}/state'.format(bridge_ip(), bridge_key, bulb_id)

    if brightness < 1 or brightness > 100:
        print('error')
    else:
        bri_lvl = int((brightness / 100) * 254)

        data = json.dumps({'on':True, "bri":bri_lvl}) # To change brightness level it requires you to switch the bulb on – maybe change this?
        result = requests.put(api_url, data)

        if 'success' in result:
            print('Bulb {0} brightness changed to {1}'.format(bulb_id, brightness))

        print(req.text)

def test():
    print('hi')

# NOTE: Discard later:

#     # Check whether request successfully completed or not
#     if not status.is_error():
#         print("no error?")
#         pass  # Message successfully published to specified channel.
#     else:
#         print("error?")
#         pass  # Handle message publish error. Check 'category' property to find out possible issue
#         # because of which request did fail.
#         # Request can be resent using: [status retry];
#
#
# class MySubscribeCallback(SubscribeCallback):
#     def presence(self, pubnub, presence):
#         pass  # handle incoming presence data
#
#     def status(self, pubnub, status):
#         if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
#             pass  # This event happens when radio / connectivity is lost
#
#         elif status.category == PNStatusCategory.PNConnectedCategory:
#             # Connect event. You can do stuff like publish, and know you'll get it.
#             # Or just use the connected event to confirm you are subscribed for
#             # UI / internal notifications, etc
#             print("sending stuff")
#             pubnub.publish().channel("sgriptchannel").message("hello!!").async(my_publish_callback)
#         elif status.category == PNStatusCategory.PNReconnectedCategory:
#             pass
#             # Happens as part of our regular operation. This event happens when
#             # radio / connectivity is lost, then regained.
#         elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
#             pass
#             # Handle message decryption error. Probably client configured to
#             # encrypt messages and on live data feed it received plain text.
#
#     def message(self, pubnub, message):
#         print(message.message)
#         pass  # Handle new message stored in message.message
#
#
# pubnub.add_listener(MySubscribeCallback())
# pubnub.subscribe().channels('sgriptchannel').execute()

#light_brightness(50, 'iPXdeY5dqiXuAavI6qVtfVzX1V1cs441EIxz9u57', 1)
#show_hues('iPXdeY5dqiXuAavI6qVtfVzX1V1cs441EIxz9u57')

#light_on()
