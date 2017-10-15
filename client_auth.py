import json
import ast
import hashlib

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub

def my_publish_callback(envelope, status):
    if not status.is_error():
        print("Client: Message successfully sent to gateway.")
    else:
        print("Client: Error transmitting message to gateway.")

class Client(SubscribeCallback):

    def __init__(self, uuid):
        self.authed = self.global_channel = False
        self.pnconfig = PNConfiguration()
        self.pnconfig.publish_key = 'pub-c-85d5e576-5d92-48b0-af83-b47a7f21739f'
        self.pnconfig.subscribe_key = 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579'
        self.pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
        self.pnconfig.ssl = True
        self.pnconfig.subscribe_timeout = self.pnconfig.connect_timeout = self.pnconfig.non_subscribe_timeout = 9^99

        self.pnconfig.uuid = uuid

        self.pubnub = PubNub(self.pnconfig)
        self.pubnub.add_listener(self)

        print("Client: Connecting to gateway to be authenticated..")
        self.pubnub.subscribe().channels(["gateway_auth"]).execute()

        self.uuid_hash = hashlib.new("sha3_512")
        encode = self.uuid_hash.update((self.pnconfig.uuid).encode("UTF-8"))
        self.channel = ""

    def publish_request(self, channel, msg):
        if type(msg) is dict:
            msg = json.loads(json.dumps(msg))
        else:
            msg = msg

        self.pubnub.publish().channel(channel).message(msg).sync()

    def enquire_modules(self, channel):
        self.publish_request(channel, {"enquiry": True})

    def enquire_module_methods(self, channel, module):
        return(self.publish_request(channel, {"enquiry": True, "module_name": module}))

    def device_request(self, channel, module_name = None, requested_function = None, parameters = False):
        jsonmsg = {"enquiry": False, "module_name": module_name, "requested_function": requested_function, "parameters": parameters}
        return(self.publish_request(channel, jsonmsg))

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            print("Client: Unexpectedly disconnected.")

        elif status.category == PNStatusCategory.PNReconnectedCategory:
            print("Client: Reconnected.")

    def message(self, pubnub, message):
        msg = message.message["Gateway"] if "Gateway" in message.message else message.message

        if not self.authed:
            uuid_hash = hashlib.new("sha3_512")
            encode = uuid_hash.update((self.pnconfig.uuid).encode("UTF-8"))

            if msg == uuid_hash.hexdigest():
                print("Client: Connecting to UUID channel to retrieve private channel information..")
                self.pubnub.subscribe().channels(self.pnconfig.uuid).execute()

            if 'auth_key' in msg:
                self.pubnub.unsubscribe().channels(self.pnconfig.uuid).execute();
                self.authed = True

                self.channel = msg['channel']
                self.pnconfig.auth_key = msg['auth_key']
                self.global_channel = msg['global_channel']

                print("Client Connecting to private channel '{}' and global channel '{}'..".format(self.channel, self.global_channel))
                self.pubnub.subscribe().channels([self.channel, self.global_channel]).execute()

                while True:
                    show_modules = input("Show modules available (Y/n)? ")
                    if show_modules == "Y":
                        self.enquire_modules(self.channel)
                        break

        elif 'enquiry' in msg.keys() and not isinstance(msg["enquiry"], bool):
                try: # Getting available modules and choosing one to get methods from.
                    if "modules" in msg["enquiry"].keys():
                        module_options = msg['enquiry']['modules']
                        show_module_methods = input("Choose a module to call methods from {}: ".format(module_options))
                        self.enquire_module_methods(self.channel, show_module_methods)

                    elif "module_methods" in msg["enquiry"].keys():
                        module_methods = msg['enquiry']['module_methods']
                        method_chosen = input("Choose a method to call {}: ".format(module_methods))
                        print("You chose: {}".format(method_chosen))

                        while True:
                            print("In corresponding order, please enter the parameters in an array below, leave blank if none:")
                            params = input()

                            if params:
                                try:
                                    self.device_request(self.channel, msg['enquiry']['module_name'], method_chosen, ast.literal_eval(params))
                                    break
                                except:
                                    print("Error: This needs to be entered in array format/comma separated, use casing for bools")
                                    pass
                            else:
                                print("Error: Please enter parameters.. If blank use []")

                except Exception as e:
                    print("error {}".format(e))

        elif 'result' in msg.keys() or 'error' in msg.keys():
            print("response retrieved: " + str(msg))
            self.enquire_modules(self.channel)

        elif message.channel == self.global_channel:
            print(message.message)

if __name__ == "__main__":
    client = Client("platypus_801")
