
'''
__author__ = "sgript"

Expected request format:
{
'enquiry': '',               # Boolean, if used all rest parameters are unneeded, module_name can be optionally checked.
'module_name': '',
'requested_function': '',
'parameters': ''
}

Policy response-back format:
{'access': 'rejected', 'request': {'user_uuid': 'client_test', 'enquiry': False, 'module_name': 'philapi', 'requested_function': 'light_switch', 'parameters': [False, 1]}}

All newly added modules go into /modules/ and are picked up by gateway.
'''

import sys
import os
import json
import inspect
from importlib import util

from helpers import module_methods, default_args, PasteFetcher, id_generator as idgen, list_modules as lm
from modules import *
from modules import help
import gateway_database
import policy_server                    # TODO: Temporary

from pubnub.enums import PNStatusCategory
from pubnub.callbacks import SubscribeCallback
from pubnub.pubnub import PubNub, SubscribeListener
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy

import subprocess

def my_publish_callback(envelope, status):
    if not status.is_error():
        print("GatewayReceiver: Message successfully sent to client.")
        pass
    else:
        print("GatewayReceiver: Error transmitting message to client.")
        pass

class Receiver(SubscribeCallback):
    def __init__(self, gdatabase = None, admin_channel = None):
        self.gdatabase = gdatabase
        self.admin_channel = admin_channel

        if gdatabase is None:
            password = input("Database password: ")
            self.gdatabase = gateway_database.GatewayDatabase(host = 'ephesus.cs.cf.ac.uk', user = 'c1312433', password = password, database = 'c1312433')

        if admin_channel is None:
            self.admin_channel = idgen.id_generator(size = 255)

        self.gdatabase.set_receiver_auth_channel(self.admin_channel)

        pnconfig = PNConfiguration()
        pnconfig.subscribe_key = self.gdatabase.sub_key()
        pnconfig.publish_key = self.gdatabase.pub_key()
        pnconfig.secret_key = self.gdatabase.sec_key()

        pnconfig.ssl = True
        pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
        pnconfig.subscribe_timeout = pnconfig.connect_timeout = pnconfig.non_subscribe_timeout = 9^99

        self.uuid = 'GR'
        pnconfig.uuid = self.uuid
        self.pubnub = PubNub(pnconfig)
        self.pubnub.add_listener(self)

        print("Rebuilding subscriptions..")
        subscriptions = self.gdatabase.get_channels()
        if subscriptions:
            self.subscribe_channels(subscriptions)

        print("GatewayReceiver: Subscribing to the Policy server and Gateway global feed..")
        self.pubnub.grant().channels(["policy"]).auth_keys([self.gdatabase.receivers_key(), self.gdatabase.policy_key()]).read(True).write(True).manage(True).ttl(0).sync()                # TODO: Temporary
        self.pubnub.grant().channels(["gateway_global", self.admin_channel]).read(True).write(True).manage(True).sync()
        self.subscribe_channels(["policy", "gateway_global", self.admin_channel])

        self.pastebin = PasteFetcher.PasteFetcher()
        ps = policy_server.PolicyServer(self.gdatabase)                                                 # TODO: Temporary

    def subscribe_channels(self, channel_name):
        print("GatewayReceiver: Subscribed to {}".format(channel_name))
        self.pubnub.subscribe().channels(channel_name).with_presence().execute()

    def publish_request(self, channel, msg):
        msg_json = json.loads(json.dumps(msg))
        self.pubnub.publish().channel(channel).message(msg_json).async(my_publish_callback)

    def presence(self, pubnub, presence):
        if presence.event == 'leave' and presence.uuid != self.uuid and presence.channel != 'policy':
            print("GatewayReceiver: {} event on channel {} by user {}, unsubscribing.".format(presence.event.title(), presence.channel, presence.uuid))
            pubnub.unsubscribe().channels(presence.channel).execute()
            self.gdatabase.gateway_subscriptions_remove(presence.channel, presence.uuid)

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            print('GatewayReceiver: Unexpectedly disconnected.')
            pubnub.publish().channel('gateway_auth').message({"Global_Message":"GatewayReceiver: Unexpectedly disconnected."}).async(my_publish_callback)

        elif status.category == PNStatusCategory.PNConnectedCategory:
            print('GatewayReceiver: Connected.')

        elif status.category == PNStatusCategory.PNReconnectedCategory:
            print("Rebuilding subscriptions..")
            subscriptions = self.gdatabase.get_channels()
            self.pubnub.subscribe().channels(subscriptions).with_presence().execute()
            print('GatewayReceiver: Reconnected.')

    def delete_defaults(self, function, array):
        defaults = default_args.get_default_args(function)
        if defaults:
            for default_arg in defaults:
                array.remove(default_arg)

    def message(self, pubnub, message):
        msg = message.message
        print(msg)


        if message.channel == self.admin_channel and "success" not in msg.keys() and "error" not in msg.keys():

            '''
            {"module_name": "x", "pastebin": "y", "installation_commands": "pip ..."}
            '''

            try:
                paste_id = msg['pastebin'].split("/")[-1]
                function_content = self.pastebin.parse_paste(paste_id)
                with open('./modules/{}.py'.format(msg['module_name']),'w') as f:

                    cmd = msg["installation_commands"].split(" ")

                    if len(cmd) > 1:
                        if "pip" is in cmd or "brew" in cmd:
                            try:
                                moduleDeclared = False
                                for param in cmd[1:]:
                                    print("function_content {}".format(function_content))
                                    if param in function_content:
                                        test = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                                        output = test.communicate()[0]
                                        moduleDeclared = True
                                        self.publish_request(self.admin_channel, {"success": "installed commands: {}".format(output), "request": message.message})
                                        break

                                if not moduleDeclared:
                                    self.publish_request(self.admin_channel, {"error": "the command you asked to run is not required in the module", "request": message.message})
                                    os.remove(f.name)
                                    return

                            except Exception as e:
                                print("GatewayReceiver: There was an issue checking for installation commands for dependencies required for new module. {}".format(e))
                                os.remove(f.name)
                                return

                                return
                        else:
                            self.publish_request(self.admin_channel, {"error": "the only acceptable package managers are pip or brew", "request": message.message})
                            os.remove(f.name)
                            return

                    f.write(function_content)
                    self.publish_request(self.admin_channel, {"success": "module {} successfully added".format(msg["module_name"]), "request": message.message})

            except KeyError:
                print("GatewayReceiver: module_name or pastebin or installation_commands was not found in the json, all required.")
                self.publish_request(self.admin_channel, {"error": "module_name, pastebin and installation_commands must be included as keys", "request": message.message})
                pass

        elif message.channel != "policy":
            if 'enquiry' in msg and msg['enquiry'] is True:
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
                    ## TEST
                    module_list = lm.list_modules()
                    uuid = self.gdatabase.get_uuid_from_channel(message.channel)
                    canaries_for_uuid = self.gdatabase.hide_canaries(uuid)

                    for canary in canaries_for_uuid: # So don't show any canaries not actually present locally
                        if canary not in module_list:
                            canaries_for_uuid.remove(canary)

                    modules_to_show =  list(set(module_list) - set(canaries_for_uuid)) if len(module_list) > len(canaries_for_uuid) else list(set(canaries_for_uuid) - set(module_list)) # only show the user canaries meant for them or all users, not another user's canaries

                    modules_to_show =  list(set(module_list) - set(canaries_for_uuid))

                    self.publish_request(message.channel, {"enquiry": {"modules": modules_to_show}})

            elif 'enquiry' in msg and msg['enquiry'] is False:
                if 'requested_function' in msg:
                    if 'module_name' in msg:
                        module_found = True if util.find_spec("modules."+msg['module_name']) != None else False

                        if module_found:
                            module = sys.modules['modules.' + msg['module_name']]

                            # Temporarily disabled
                            method_requested = getattr(module, msg['requested_function'])
                            method_args = inspect.getargspec(method_requested)[0]

                            self.delete_defaults(method_requested, method_args)
                            if isinstance(msg['parameters'], list) and len(msg['parameters']) == len(method_args):
                                get_mac = getattr(module, 'get_mac')
                                mac_address = get_mac()

                                self.publish_request("policy", {"channel": message.channel, "mac_address": mac_address, "request": msg})

                            else:
                                self.publish_request(message.channel, {"error": "Your request's parameters must be an array and match required parameters of the method."})


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

            elif "canary_breach" in msg:
                if msg["canary_breach"]["action"] == "shutdown_now":
                    print("GatewayReceiver: Received shutdown command.")
                    self.publish_request(self.admin_channel, {"command": "shutdown_now"})
                    os._exit(1)

            elif "canary" in msg:
                paste_id = msg['canary']['pastebin'].split("/")[-1]
                function_content = self.pastebin.parse_paste(paste_id)
                with open('./modules/{}.py'.format(msg['canary']['canary_name']),'w') as f:
                    f.write(function_content)

            pass

if __name__ == "__main__":
    receiver = Receiver()
