'''
__author__ = "@sgript"

'''
import requests
import json


class ButtonNotPressed(Exception):
    pass

bulb_key = "PEuzGOSH9rFqcjqDOCREmpeBpdT-kc-zbFY3tyXh"

def bridge_ip():
    list_bridges = requests.get('https://www.meethue.com/api/nupnp')
    bridge_ip = json.loads(list_bridges.text) # string to json

    if bridge_ip:
        bridge_ip = bridge_ip[0]['internalipaddress']

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

    bulbs = json.loads(req.text)

    bulbs_available = {}
    for bulb_id in bulbs:
         bulbs_available[bulbs[bulb_id]['name']] = bulb_id

    return bulbs_available

def light_switch(state, bulb_id, bridge_key = bulb_key):
    """state: True or False, bulb_id: E.g. 1 -> [True, 1] -- Turn bulb 1 on"""
    api_url = 'http://{0}/api/{1}/lights/{2}/state'.format(bridge_ip(), bridge_key, bulb_id)
    data = json.dumps({"on":state})
    req = requests.put(api_url, data)

    return req.text

def light_brightness(state, bulb_id, bridge_key = bulb_key):
    """state: 50, bulb_id: E.g. 1 -> [50, 1] -- 50 percent brightness on bulb 1"""
    api_url = 'http://{0}/api/{1}/lights/{2}/state'.format(bridge_ip(), bridge_key, bulb_id)

    if state < 1 or state > 100:
        return {"error": "light brightness should be between 1 or 100"}
    else:
        bri_lvl = int((state / 100) * 254) # level gets changed to percentage equivalence out of 254 (max brightness for hues)

        data = json.dumps({'on':True, "bri":bri_lvl}) # if changing brightness bulb must be turned on.
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
