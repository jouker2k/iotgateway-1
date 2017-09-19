import json
import ast
import hashlib

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy
from pubnub.pubnub import PubNub

# TODO: User UUID currently has to be sent by Client, perhaps DB can auto-check this by checking which channel belongs to which user.

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

    def device_request(self, channel, enquiry_bool, module_name = None, requested_function = None, parameters = False):
        jsonmsg = {"user_uuid": self.pnconfig.uuid, "enquiry": enquiry_bool, "module_name": module_name, "requested_function": requested_function, "parameters": parameters}
        return(self.publish_request(channel, jsonmsg))

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            print("Client: Unexpectedly disconnected.")

        elif status.category == PNStatusCategory.PNReconnectedCategory:
            print("Client: Reconnected.")

    def message(self, pubnub, message):
        if not self.authed:
            uuid_hash = hashlib.new("sha3_512")
            encode = uuid_hash.update((self.pnconfig.uuid).encode("UTF-8"))

            if message.message == uuid_hash.hexdigest():
                print("Client: Connecting to UUID channel to retrieve private channel information..")
                self.pubnub.subscribe().channels(self.pnconfig.uuid).execute()

            if 'auth_key' in message.message:
                self.pubnub.unsubscribe().channels(self.pnconfig.uuid).execute();

                self.channel = message.message['channel']
                self.pnconfig.auth_key = message.message['auth_key']
                self.global_channel = message.message['global_channel']
                self.authed = True

                print("Client Connecting to private channel '{}' and global channel '{}'..".format(self.channel, self.global_channel))
                self.pubnub.subscribe().channels([self.channel, self.global_channel]).execute()

                show_modules = input("Show modules available (Y/n)? ")
                if show_modules is "Y":
                    self.enquire_modules(self.channel)

        elif 'enquiry' in message.message:
                try: # Getting available modules and choosing one to get methods from.
                    module_options = message.message['enquiry']['modules']
                    show_module_methods = input("Choose a module to call methods from {}: ".format(module_options))
                    self.enquire_module_methods(self.channel, show_module_methods)
                except:
                    pass

                try:
                    module_methods = message.message['enquiry']['module_methods']
                    method_chosen = input("Choose a method to call {}: ".format(module_methods))
                    print("You chose: {}".format(method_chosen))

                    print("In corresponding order, please enter the parameters in an array below, leave blank if none:")
                    params = input()

                    if params:
                        self.device_request(self.channel, False, message.message['enquiry']['module_name'], method_chosen, ast.literal_eval(params))
                        pass
                except:
                    pass

        elif 'result' or 'error' in message.message:
            print("response retrieved: " + str(message.message))
            self.enquire_modules(self.channel)

        if message.channel == self.global_channel:
            print(message.message)

if __name__ == "__main__":
    client = Client("platypus_17")
