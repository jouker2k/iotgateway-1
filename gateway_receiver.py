
'''
__author__ = "sgript"

Expected request format:
{
'enquiry': '',               # Boolean, if used all rest parameters are unneeded, module_name can be optionally checked.
'module_name': '',           # Use this to find applicable methods?
'id': '',                    # If applicable, i.e. Philips Hue
'device_type': '',           # Will define fixed categories later.
'requested_function': '',    # NOTE: See ast module ***
'parameters': ''
}

# NOTE: When just listing devices all parameters can be

TODO: This is to be handled by a single-service function (likely messages) branching to applicable functions.

'''

import sys
import json
import inspect
from importlib import util

from helpers import module_methods, default_args, list_modules as lm
from modules import *
from modules import help
import gateway_database
import policy_server

from pubnub.enums import PNStatusCategory
from pubnub.callbacks import SubscribeCallback
from pubnub.pubnub import PubNub, SubscribeListener
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy


def my_publish_callback(envelope, status):
    if not status.is_error():
        print("GatewayReceiver: Message successfully sent to client.")
        pass
    else:
        print("GatewayReceiver: Error transmitting message to client.")
        pass

class Receiver(SubscribeCallback):
    def __init__(self):
        # TODO: Perhaps do default params for GR so if it's being called by Auth then it doesn't create new instances/saves resources, however if called independent, parameters would be used.. + Idea: Second constructor?

        password = input("Database password: ")
        host = 'ephesus.cs.cf.ac.uk'
        user = 'c1312433'
        database = 'c1312433'

        print("GatewayReceiver: Starting gateway database..")
        gd = gateway_database.GatewayDatabase(host, user, password, database)

        pnconfig = PNConfiguration()


        pnconfig.subscribe_key = gd.sub_key()
        pnconfig.publish_key = gd.pub_key()
        pnconfig.auth_key =  gd.receivers_key()
        pnconfig.secret_key = gd.sec_key()

        pnconfig.uuid = 'GR'
        pnconfig.ssl = True
        pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
        pnconfig.subscribe_timeout = pnconfig.connect_timeout = pnconfig.non_subscribe_timeout = 9^99

        self.pubnub = PubNub(pnconfig)
        self.pubnub.add_listener(self)

        print("GatewayReceiver: Subscribing to the Policy server..")
        self.pubnub.grant().channels("policy").auth_keys([pnconfig.auth_key, gd.policy_key()]).read(True).write(True).manage(True).ttl(0).sync()
        self.subscribe_channel("policy")

        ps = policy_server.PolicyServer()
        # TODO: On init need to subscribe to all channels required to recover from crashes.

    def subscribe_channel(self, channel_name):
        print("GatewayReceiver: Subscribed to {}".format(channel_name))
        self.pubnub.subscribe().channels(channel_name).with_presence().execute()

    def publish_request(self, channel, msg):
        # REVIEW: May need to format py to json
        msg_json = json.loads(json.dumps(msg))
        self.pubnub.publish().channel(channel).message(msg_json).async(my_publish_callback)

    def presence(self, pubnub, presence):
        #print(presence.channel)
        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            print('GatewayReceiver: Unexpectedly disconnected.')

        elif status.category == PNStatusCategory.PNConnectedCategory:
            print('GatewayReceiver: Connected.')

        elif status.category == PNStatusCategory.PNReconnectedCategory:
            print('GatewayReceiver: Reconnected.')

    def delete_defaults(self, function, array):
        defaults = default_args.get_default_args(function)
        if defaults:
            for default_arg in defaults:
                array.remove(default_arg)

    def message(self, pubnub, message):
        msg = message.message
        print(msg)
        if message.channel != "policy":
            if 'enquiry' in msg and msg['enquiry'] is True:
                # TODO: Still need something to list available modules.
                if 'module_name' in msg:
                    module_found = True if util.find_spec("modules."+msg['module_name']) != None else False

                    # Maybe since there was something supplied, instead of False just call a publish to tell them
                    # They mispelled or something.

                    if module_found:

                        methods = module_methods.find(msg['module_name']) # Gets module's methods (cannot be inside a class)

                        module = sys.modules['modules.' + msg['module_name']]

                        dictionary_of_functions = {}
                        for method in methods:
                            function = getattr(module, method)
                            dictionary_of_functions[method] = inspect.getargspec(function)[0]

                            # Going to remove any default parameters - no need to supply keys etc.
                            self.delete_defaults(function, dictionary_of_functions[method])

                        enquiry_response = {"enquiry": {"module_name": msg['module_name'], "module_methods": dictionary_of_functions}}

                        self.publish_request(message.channel, enquiry_response)

                # Else if no module name supplied just show list of them available.
                elif 'module_name' not in msg and msg['enquiry'] is True:

                    self.publish_request(message.channel, {"enquiry": {"modules": lm.list_modules()}})

            elif 'enquiry' in msg and msg['enquiry'] is False:
                    if 'requested_function' in msg:
                        if 'module_name' in msg:
                            module_found = True if util.find_spec("modules."+msg['module_name']) != None else False

                            if module_found:
                                module = sys.modules['modules.' + msg['module_name']]

                                # Temporarily disabled
                                method_requested = getattr(module, msg['requested_function'])
                                method_args = inspect.getargspec(method_requested)[0]

                                if not msg['parameters'] and method_args is not None: # needs params but not provided
                                    print('{}: User did not provide parameters that the method requires!'.format(message.channel))

                                    result = {'result': method_requested()}
                                    self.publish_request(message.channel, result)

                                elif msg['parameters'] and method_args is not None: # params provided and needed

                                    get_mac = getattr(module, 'get_mac')
                                    mac_address = get_mac()

                                    self.publish_request("policy", {"channel": message.channel, "mac_address": mac_address, "request": msg})

                                    # REVIEW: Useful later when granted access
                                    #result = method_requested(*msg['parameters'])
                                    #jsonres = {"result": str(result)}
                                    #self.publish_request(message.channel, jsonres)


                        else:
                            print("{}: Error no module name supplied even when not an enquiry".format(message.channel)) # tidy up later

            # TODO: Below error works, but can be erroneous, so will need to checked
            # Could be triggered by receiver itself, so just checking for "error" in msg
            # to trigger it, may not be enough.
            # else:
            #     if "error" not in msg:
            #         error_msg = {"error": "There was an issue, your JSON does not contain the correct request information."}
            #         self.publish_request(message.channel, error_msg)

        elif message.channel == "policy":
            # {'access': 'rejected', 'request': {'user_uuid': 'client_test', 'enquiry': False, 'module_name': 'philapi', 'requested_function': 'light_switch', 'parameters': [False, 1]}}

            if "access" in msg:

                if msg["access"] == "granted":
                    print("Access on {} granted, with the request: {}".format(msg['channel'], msg['request']))
                    module = sys.modules['modules.' + msg['request']['module_name']]
                    method_requested = getattr(module, msg['request']['requested_function'])
                    result = method_requested(*msg['request']['parameters'])

                    self.publish_request(msg['channel'], {"module_name": msg['request']['module_name'], "requested_function": msg['request']['requested_function'], "result": result})

                else:
                    print("Access on {} rejected, with the request: {}".format(msg['channel'], msg['request']))
                    self.publish_request(msg['channel'], {"module_name": msg['request']['module_name'], "requested_function": msg['request']['requested_function'], "result": "rejected"})


# if __name__ == "__main__":
#     receiver = Receiver()
#     receiver.subscribe_channel('NO40ACE6I6', 'V3SIPF92JQ')
    # TTL needs to be 0
