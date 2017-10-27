'''
__author__ = "@sgript"

Example JSONs:
* Remotely create a new module:
{"module_name": "test_module", "pastebin": "https://pastebin.com/7wuPW4yd", "installation_commands": "pip install bs4"}

* Enquiry of modules:
{"enquiry": True}

* Enquiry of functions for a module:
{"enquiry": True, "module_name": "philapi"}

* Make a device request:
{"enquiry": false, "module_name": "philapi", "requested_function": "nonexistent_function", "parameters": [true, 1]}
'''

import sys
import os
import json
import inspect
from importlib import util

from helpers import module_methods, default_args, PasteFetcher, id_generator as idgen, list_modules as lm
from exceptions import exceptions
from modules import *
from modules import help
import gateway_database
#from PolicyServer import policy_server

from pubnub.enums import PNStatusCategory # To see status of publishes sent - if succeeded etc.
from pubnub.callbacks import SubscribeCallback # Subscription loop to continoulsy see messages.
from pubnub.pubnub import PubNub, SubscribeListener # Not a subsciption loop, used for testing
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy # Configuration of keys, setting UUID, reconnection procedure

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

        self.default_channels = ["policy", "gateway_global", self.admin_channel, "embedded_devices"]

        print("GatewayReceiver: Subscribing to the Policy server and Gateway global feed..")
        self.pubnub.grant().channels(self.default_channels[0]).auth_keys([self.gdatabase.receivers_key(), self.gdatabase.policy_key()]).read(True).write(True).manage(True).ttl(0).sync()
        self.pubnub.grant().channels(self.default_channels[1:]).read(True).write(True).manage(True).sync()

        self.subscribe_channels(self.default_channels[:-1])

        self.pastebin = PasteFetcher.PasteFetcher()
        #ps = policy_server.PolicyServer(self.gdatabase)

    def subscribe_channels(self, channel_name):
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
            pubnub.publish().channel('gateway_global').message({"Global_Message":"GatewayReceiver: Unexpectedly disconnected."}).async(my_publish_callback)

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

        if message.channel == self.admin_channel and "success" not in msg.keys() and "error" not in msg.keys(): # install modules remotely

            usable_packages = ["pip", "brew"]

            try:
                paste_id = msg['pastebin'].split("/")[-1]
                function_content = self.pastebin.parse_paste(paste_id)
                with open('./modules/{}.py'.format(msg['module_name']),'w') as f:

                    cmd = msg["installation_commands"].split(" ") # capable of multiple installation commands for newly added modules

                    if len(cmd) > 1:
                        if cmd[0] in usable_packages:
                            try:
                                moduleDeclared = False

                                multi_commands = msg["installation_commands"].split(";")
                                if len(multi_commands) <= 1:
                                    for param in cmd[1:]:
                                        if param in function_content:
                                            moduleDeclared = True
                                            test = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                                            output = test.communicate()[0]
                                            print("GatewayReceiver: Installed: {}".format(output))
                                            break

                                else: # If multiple dependencies to install, separated via ;
                                    # So at this point we might have param in for loop like pip install x;pip install y as: pip install x then pip install y etc.
                                    for param in multi_commands:
                                        if param.split(" ")[0] in usable_packages:
                                            for arg in param.split(" "):
                                                if arg in function_content:
                                                    moduleDeclared = True
                                                elif "install" not in arg and arg not in usable_packages:
                                                    print("GatewayReceiver: Cannot install: {}, not present in the module file.".format(arg))
                                                    moduleDeclared = False
                                                    break

                                            # So once we've passed through each command between ;'s and it is legal, we just run it.
                                            if  moduleDeclared:
                                                params_array = list(filter((";").__ne__, param.split(" "))) # Removes the ; from array  https://stackoverflow.com/a/1157160
                                                test = subprocess.Popen(params_array, stdout=subprocess.PIPE)
                                                output = test.communicate()[0]
                                                print("GatewayReceiver: Installed: {}".format(output))

                                            else:
                                                break

                                        else:
                                            self.publish_request(self.admin_channel, {"error": "the only acceptable package managers are pip or brew", "request": message.message})
                                            os.remove(f.name)
                                            return

                                if not moduleDeclared:
                                    self.publish_request(self.admin_channel, {"error": "the command you asked to run is not required in the module", "request": message.message})
                                    os.remove(f.name)
                                    return
                                else:
                                    self.publish_request(self.admin_channel, {"success": "installed commands: {}".format(msg["installation_commands"]), "request": message.message})

                            except Exception as e:
                                print("GatewayReceiver: There was an issue checking for installation commands for dependencies required for new module. {}".format(e))
                                os.remove(f.name)
                                return
                        else:
                            self.publish_request(self.admin_channel, {"error": "the only acceptable package managers are pip or brew", "request": message.message})
                            os.remove(f.name)
                            return

                    f.write(function_content) # once validation checks out, make the physical module
                    self.publish_request(self.admin_channel, {"success": "module {} successfully added".format(msg["module_name"]), "request": message.message})

            except KeyError:
                print("GatewayReceiver: module_name or pastebin or installation_commands was not found in the json, all required.")
                self.publish_request(self.admin_channel, {"error": "module_name, pastebin and installation_commands must be included as keys", "request": message.message})
                pass

        elif message.channel not in self.default_channels and "error" not in msg: # handle regular user requests here

            # Check if more than 1 person in channel + determine their UUID
            envelope = pubnub.here_now().channels(message.channel).include_uuids(True).sync()

            users = envelope.result.channels[0].occupants
            users_in_channel = envelope.result.total_occupancy
            user_uuid = None

            if users_in_channel > 2:
                self.publish_request(message.channel, {"Gateway":{"error": "There are multiple users in this channel"}})
                return

            else:
                for occupant in users:
                    if occupant.uuid != self.uuid:
                        user_uuid = occupant.uuid # Going to take the user's UUID who is in the channel and use it for verification.
                        break

            blacklisted = self.gdatabase.check_blacklisted(message.channel, user_uuid)
            if blacklisted: # check if auth_blacklisted -> means no access whatsoever
                self.publish_request(message.channel, {"Gateway":{"error": "Blacklisted from all requests."}})
                return

            try:
                if 'enquiry' in msg.keys() and msg['enquiry'] is True: # request to show available modules or functions for a module
                    if 'module_name' in msg:
                        module_found = True if util.find_spec("modules."+msg['module_name']) != None else False


                        if module_found:
                            try:
                                methods = module_methods.find(msg['module_name']) # Gets module's methods (cannot be inside a class)

                                module = sys.modules['modules.' + msg['module_name']]
                                dictionary_of_functions = {}
                                for method in methods:
                                    function = getattr(module, method)
                                    dictionary_of_functions[method] = inspect.getargspec(function)[0]

                                    # Going to remove any default parameters - no need to supply keys etc.
                                    self.delete_defaults(function, dictionary_of_functions[method])

                                enquiry_response = {"enquiry": {"module_name": msg['module_name'], "module_methods": dictionary_of_functions}} # show available modules' functions/methods

                                self.publish_request(message.channel, {"Gateway": enquiry_response})

                            except KeyError:
                                self.publish_request(message.channel, {"Gateway": {"error": "Module {} or function {} not found".format(msg['module_name'], msg['module_methods'])}})

                        else:
                            self.publish_request(message.channel, {"Gateway":{"error": "Module {} was not found.".format(msg['module_name'])}})

                    # Else if no module name supplied just show list of them available.
                    elif 'module_name' not in msg and msg['enquiry'] is True:
                        module_list = lm.list_modules()
                        canaries_for_uuid = self.gdatabase.hide_canaries(user_uuid) # We retrieve the canaries that are not meant for the users then hide them (below)

                        for canary in canaries_for_uuid: # So don't show any canaries not actually present locally
                            if canary not in module_list:
                                canaries_for_uuid.remove(canary)

                        modules_to_show =  list(set(module_list) - set(canaries_for_uuid)) if len(module_list) > len(canaries_for_uuid) else list(set(canaries_for_uuid) - set(module_list)) # only show the user canaries meant for them or all users, not another user's canaries

                        #modules_to_show =  list(set(module_list) - set(canaries_for_uuid))

                        self.publish_request(message.channel, {"Gateway": {"enquiry": {"modules": modules_to_show}}})

                # process user device request (non-enquiry)
                elif 'enquiry' in msg.keys() and msg['enquiry'] is False:
                    if 'requested_function' in msg:
                        if 'module_name' in msg:
                            module_found = True if util.find_spec("modules."+msg['module_name']) != None else False

                            if module_found:
                                module = sys.modules['modules.' + msg['module_name']]

                                try:
                                    method_requested = getattr(module, msg['requested_function'])
                                    method_args = inspect.getargspec(method_requested)[0]

                                    self.delete_defaults(method_requested, method_args)
                                    if isinstance(msg['parameters'], list) and len(msg['parameters']) == len(method_args):

                                        mac_address = ''
                                        try:
                                            get_mac = getattr(module, 'get_mac')
                                            mac_address = get_mac()
                                        except:
                                            mac_address = '0'
                                            print("GatewayReceiver: Module {} does not have get_mac(), searching with 0 instead".format(msg['module_name']))

                                        finally: # after validation checks out, give to policy server to verify security
                                            msg["user_uuid"] = user_uuid
                                            self.publish_request("policy", {"channel": message.channel, "mac_address": mac_address, "request": msg})

                                    else:
                                        self.publish_request(message.channel, {"Gateway": {"error": "Your request's parameters must be an array and match required parameters of the method."}})

                                except:
                                    self.publish_request(message.channel, {"Gateway": {"error": "Module {} has no function {}".format(msg['module_name'], msg['requested_function'])}})
                            else:
                                self.publish_request(message.channel, {"Gateway": {"error": "Module {} not found".format(msg['module_name'])}})

                        else:
                            print("{}: Error no module name supplied even when not an enquiry".format(message.channel)) # tidy up later
                            raise exceptions.BadFormat("Module must be in non-enquiry request.")
                    else:
                        raise exceptions.BadFormat("Requested function must be in non-enquiry request.")

            except exceptions.BadFormat as error:
                error_msg = {"Gateway": {'error': str(error), "correct_format": {"user_uuid": "", "enquiry": "", "module_name": "", "requested_function": "", "param": ""}}}
                self.publish_request(message.channel, error_msg)

            except Exception as e:
                print("GatewayReceiverError: {}".format(e))

        elif message.channel == "policy": # respond accordingly depending on policy's decisions
            if "access" in msg.keys():

                if msg["access"] == "granted":
                    if msg['request']['module_name'] == "controlpi":
                        msg['request']['parameters'] = msg['request']['parameters'] + [self.gdatabase.embedded_devices_key()]

                    module = sys.modules['modules.' + msg['request']['module_name']]
                    method_requested = getattr(module, msg['request']['requested_function'])
                    result = method_requested(*msg['request']['parameters']) # execute user's requested function

                    self.publish_request(msg['channel'], {"Gateway": {"module_name": msg['request']['module_name'], "requested_function": msg['request']['requested_function'], "result": result}})

                else: # rejection message or if requested to emergency shutdown by policy server
                    rejection_msg = {"Gateway": {"module_name": msg['request']['module_name'], "requested_function": msg['request']['requested_function'], "result": "rejected"}}

                    if "shutdown_now" in msg["access"]:
                        print("GatewayReceiver: Received shutdown command.")
                        self.pubnub.publish().channel(msg['channel']).message(rejection_msg).sync()
                        self.pubnub.publish().channel(self.admin_channel).message({"command": "shutdown_now"}).sync()
                        os._exit(1)

                    else:
                        self.publish_request(msg['channel'], rejection_msg)

            elif "canary" in msg.keys(): # process command from policy to create physical canary file, processed from pastebin code.
                paste_id = msg['canary']['pastebin'].split("/")[-1]
                function_content = self.pastebin.parse_paste(paste_id)
                with open('./modules/{}.py'.format(msg['canary']['canary_name']),'w') as f:
                    f.write(function_content)

            elif "error" in msg.keys():
                self.publish_request(msg['channel'], {"error": msg['error']})

if __name__ == "__main__":
    receiver = Receiver()
