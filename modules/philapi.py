import requests
import json
# from .exceptions import *
from exceptions import exception

# TODO: HANDLE RESPONSES TO GIVE TO CLIENT (ERROR CODES)
# TODO: For Philips API calls do better error returns, such as passing on those returned via the API.

# REVIEW TEMPORARY PLACEMENT OF KEY
bulb_key = "PEuzGOSH9rFqcjqDOCREmpeBpdT-kc-zbFY3tyXh"

def bridge_ip():
    list_bridges = requests.get('https://www.meethue.com/api/nupnp')
    bridge_ip = json.loads(list_bridges.text) # string to json
    if len(bridge_ip) > 1:
        # TODO: Selection screen maybe here, if multiple IPs (multiple bridges) detected..
        pass
    else:
        bridge_ip = bridge_ip[0]['internalipaddress'] # if just one bridge, take its ip

    print(bridge_ip)
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
                raise exception.ButtonNotPressed
            else:
                # once button has been pressed, we can make a successful request.
                data = json.dumps({"devicetype":"my_hue_app#"+bridge_name})
                result = json.loads(requests.post(api_url, data).text)[0]

                if 'error' in result:
                    raise exception.ButtonNotPressed
                else:
                    print('The key found is: ' + result['success']['username'])
                    result = result['success']['username']
                    break

        except exception.ButtonNotPressed as e:
            print('There was an error, please try press the button again.')
            continue

    return result

def show_hues(bridge_key = bulb_key):
    # TODO: REPLACE HARDCODED AUTH KEY WITH RETRIEVED ONE --> bridge_auth()
    req = requests.get('http://{0}/api/{1}/lights'.format(bridge_ip(), bridge_key))

    # like in bridge_auth_key func will need to dump the json using dumps() then use loads()
    bulbs = json.loads(req.text)
    print(bulbs)
    bulbs_available = []
    for bulb_id in bulbs:
        print("Bulb ID: " + bulb_id + " (Name: {})".format(bulbs[bulb_id]['name'])) # perhaps make this into a JSON instead for client's convenience

    print(', '.join(map(str, bulbs_available)))

def light_switch(state, bulb_id, bridge_key = bulb_key):
    api_url = 'http://{0}/api/{1}/lights/{2}/state'.format(bridge_ip(), bridge_key, bulb_id)
    data = json.dumps({"on":state})
    req = requests.put(api_url, data)

    return(req.text)

def light_brightness(state, bulb_id, bridge_key = bulb_key):
    api_url = 'http://{0}/api/{1}/lights/{2}/state'.format(bridge_ip(), bridge_key, bulb_id)

    if state < 1 or state > 100:
        print('error')
    else:
        bri_lvl = int((state / 100) * 254)

        data = json.dumps({'on':True, "bri":bri_lvl}) # To change brightness level it requires you to switch the bulb on – maybe change this?
        result = requests.put(api_url, data)

        if 'success' in result:
            print('Bulb {0} brightness changed to {1}'.format(bulb_id, state))

        print(req.text)

def get_device_info(bulb_id, state_type, bridge_key = bulb_key):
    api_url = 'http://{0}/api/{1}/lights/{2}'.format(bridge_ip(), bridge_key, bulb_id)
    req = requests.get(api_url)
    jsonresp = json.loads(req.text)
    # So essentially all functions in thos module can send the state to this function
    # And it will builf up a key-val pair to say the type of the state and the state value
    response = json.loads(json.dumps({"device_id": jsonresp['uniqueid'], "state": {"state_type": state_type, "state_value": jsonresp['state'][state_type]}}))
    print(response)
    return response # this is going to be sent back to gateway receiver and it will check before calling other methods.

#temp
#get_device_info(1, "on", "PEuzGOSH9rFqcjqDOCREmpeBpdT-kc-zbFY3tyXh")
