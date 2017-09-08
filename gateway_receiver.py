
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
from importlib import util
import json
from helpers import module_methods, list_modules as lm
from modules import philapi

from pubnub.enums import PNStatusCategory
from pubnub.callbacks import SubscribeCallback
from pubnub.pubnub import PubNub, SubscribeListener
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy


def my_publish_callback(envelope, status):
    if not status.is_error():
        print("message err")
        pass
    else:
        print("message success")
        pass

class Receiver(SubscribeCallback):
    def __init__(self):
        # TODO: Need to define a way to find this auth key.
        # Passed straight from the gateway_auth?
        # Text file?
        # Etc. IMPORTANT
        self.pnconfig = PNConfiguration()
        self.channel = '' # REVIEW: PROBABLY DO NOT NEED THIS HERE
        self.pnconfig.uuid = self.uuid = 'gateway'
        self.pnconfig.subscribe_key = self.subscribe_key = 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579'
        self.pnconfig.publish_key = self.publish_key = 'pub-c-85d5e576-5d92-48b0-af83-b47a7f21739f'
        self.pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
        self.pnconfig.ssl = True
        self.pnconfig.subscribe_timeout = self.pnconfig.connect_timeout = self.pnconfig.non_subscribe_timeout = 9^99
        self.pubnub = PubNub(self.pnconfig)

    def subscribe_channel(self, channel_name, auth_key):
        self.pnconfig.auth_key = auth_key
        self.channel = channel_name
        self.pubnub = PubNub(self.pnconfig)
        self.pubnub.add_listener(self)

        self.pubnub.subscribe().channels(channel_name).execute()

    def presence(self, pubnub, presence):
        #print(presence.channel)
        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            print('connected?')
            pass

        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass

        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass

    def message(self, pubnub, message):
        msg = message.message

        if 'enquiry' in msg and msg['enquiry'] is True:
            # TODO: Still need something to list available modules.
            if 'module_name' in msg:
                module_found = True if util.find_spec("modules."+msg['module_name']) != None else False

                # Maybe since there was something supplied, instead of False just call a publish to tell them
                # They mispelled or something.

                if module_found:
                    # (1) Get module's methods (cannot be inside a class)
                    methods = module_methods.find(msg['module_name']) # NOTE: May not need this if using the below (getattr)


                    # (2) This will get a class's methods and actually allow you to run them
                    # Although I got the names above, this will actually help RUN them–KEEP/Use.
                    # NOTE:

                    # >>> app = sys.modules['modules.philips_api']
                    # >>> fn = getattr(app, 'test')
                    # >>> test
                    # Traceback (most recent call last):
                    #   File "<stdin>", line 1, in <module>
                    # NameError: name 'test' is not defined
                    # >>> test()
                    # Traceback (most recent call last):
                    #   File "<stdin>", line 1, in <module>
                    # NameError: name 'test' is not defined
                    # >>> fn()
                    # hi
                    module = sys.modules['modules.' + msg['module_name']]

                    dictionary_of_functions = {}
                    for method in methods:
                        function = getattr(module, method)
                        dictionary_of_functions[method] = list(function.__code__.co_varnames)

                    available_functions_resp = json.loads(json.dumps(dictionary_of_functions))

                    pubnub.publish().channel(message.channel).message(available_functions_resp).async(my_publish_callback)

                    # (3) This will get the arguments:
                    # print(zn.__code__.co_varnames)


            # Else if no module name supplied just show list of them available.
            else:
                dictionary_of_modules = json.loads(json.dumps({"modules": lm.list_modules()}))

                pubnub.publish().channel(message.channel).message(dictionary_of_modules).async(my_publish_callback)


        else:
            # TODO: Handle error message/publish back
            pass


        # TODO: IMPORTANT: Before carrying out calls, need to negotiate some security policy...

        print(message.message)
        pass


if __name__ == "__main__":
    receiver = Receiver()
    receiver.subscribe_channel('NO40ACE6I6', 'V3SIPF92JQ')
