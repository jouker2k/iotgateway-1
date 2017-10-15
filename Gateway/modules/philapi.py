import requests
import json
# from .exceptions import *
# from .exceptions import exception

# TODO: For Philips API calls do better error returns, such as passing on those returned via the API.

# TODO PLACEMENT OF KEY
bulb_key = "PEuzGOSH9rFqcjqDOCREmpeBpdT-kc-zbFY3tyXh"

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
    req = requests.get('http://{0}/api/{1}/lights'.format(bridge_ip(), bridge_key))

    # like in bridge_auth_key func will need to dump the json using dumps() then use loads()
    bulbs = json.loads(req.text)

    bulbs_available = {}
    for bulb_id in bulbs:
         bulbs_available[bulbs[bulb_id]['name']] = bulb_id

    #print(', '.join(map(str, bulbs_available)))
    return bulbs_available

def light_switch(state, bulb_id, bridge_key = bulb_key):
    api_url = 'http://{0}/api/{1}/lights/{2}/state'.format(bridge_ip(), bridge_key, bulb_id)
    data = json.dumps({"on":state})
    req = requests.put(api_url, data)

    return req.text

def light_brightness(state, bulb_id, bridge_key = bulb_key):
    api_url = 'http://{0}/api/{1}/lights/{2}/state'.format(bridge_ip(), bridge_key, bulb_id)

    if state < 1 or state > 100:
        return {"error": "light brightness should be between 1 or 100"}
    else:
        bri_lvl = int((state / 100) * 254)

        data = json.dumps({'on':True, "bri":bri_lvl}) # To change brightness level it requires you to switch the bulb on – maybe change this?
        result = requests.put(api_url, data)

        if 'success' in result:
            print('Bulb {0} brightness changed to {1}'.format(bulb_id, state))

        return result.text

def get_mac():
    global bulb_key
    api_url = 'http://{0}/api/{1}'.format(bridge_ip(), bulb_key)
    req = requests.get(api_url)
    jsonresp = json.loads(req.text)

    mac = jsonresp['config']['mac']
    return mac

#temp
#device_info(1, "on", True, "PEuzGOSH9rFqcjqDOCREmpeBpdT-kc-zbFY3tyXh")
# print(light_switch(False, 1))
