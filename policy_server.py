import json
import policy_database

from pubnub.enums import PNStatusCategory
from pubnub.callbacks import SubscribeCallback
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy

import sys, os
from helpers import module_methods

import send_email

def my_publish_callback(envelope, status):
    if not status.is_error():
        pass
    else:
        pass

class PolicyServer(SubscribeCallback):

    def __init__(self, gdatabase):
        self.pnconfig = PNConfiguration()
        self.pnconfig.uuid = 'GP'
        self.pnconfig.subscribe_key = gdatabase.sub_key()
        self.pnconfig.publish_key = gdatabase.pub_key()
        self.pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
        self.pnconfig.ssl = True
        self.pnconfig.subscribe_timeout = self.pnconfig.connect_timeout = self.pnconfig.non_subscribe_timeout = 9^99

        self.pnconfig.auth_key = 'policy_key' # later store elsewhere
        self.pubnub = PubNub(self.pnconfig)

        self.pubnub.add_listener(self)
        self.pubnub.subscribe().channels('policy').execute()

        self.pd = policy_database.PolicyDatabase(gdatabase.host, gdatabase.user, gdatabase.password, gdatabase.database)
        self.se = send_email.Alert(self.pd)

    def presence(self, pubnub, presence):

        # TODO:
        #
        # If presence seen that of anyone other than the gateway
        # Email alert.
        #

        pass  # handle incoming presence data


    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            print("PolicyServer: Unexpecrted Disconnection.")
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            print("PolicyServer: Connected.")
            pass

        elif status.category == PNStatusCategory.PNReconnectedCategory:
            print("PolicyServer: Reconnected.")
            pass

    '''device_id expected to be MAC address'''
    def message(self, pubnub, message):
        msg = message.message

        if 'policy_admin' in msg:
            method_to_call = getattr(self.pd, msg['policy_admin']['requested_function'])
            result = method_to_call(*msg['policy_admin']['parameters'])


            if method_to_call != getattr(self.pd, "canary_entry"):
                self.publish_message(message.channel, {"policy_admin_result": str(result)})
            else:
                # {"policy_admin": {"requested_function": "canary_entry", "parameters": ["testfile", "B"], "pastebin": "url"}}
                # send this response to gateway
                # gateway parses pastebin, takes content
                # creates file with this content
                # puts into the modules folder


                self.publish_message('policy', {"canary": msg['policy_admin']})

                # TODO: {'canary': {'requested_function': 'file_reading', 'parameters': ['testfile', 'B'], 'pastebin': 'https://pastebin.com/RuYyiMwj'}}
                # Also note we need to remove the `parameters` key now, unneeded when sent to receiver.

        elif 'access' not in msg: #if msg['access']:
            if msg['request']['module_name'] != 'help':
                if 'user_uuid' in msg['request'] and 'mac_address' in msg:

                    access = self.pd.access_device(msg['channel'], msg['mac_address'], msg['request']['user_uuid'], msg['request']['module_name'], msg['request']['requested_function'], msg['request']['parameters'])

                    status = "granted" if access[0] is True else "rejected: {}".format(access[1])

                    self.publish_message(message.channel, {"access": status, "channel": msg['channel'], "request": msg['request']})
                    self.pd.access_log(msg['request']['user_uuid'], msg['channel'], msg['request']['module_name'], msg['request']['requested_function'], msg['request']['parameters'], status)

                    print("PolicyServer: Access on {} by {} logged as {}".format(msg['channel'], msg['request']['user_uuid'], status))

                    if "canary_breach" in access[1]:
                        action = access[1].split(":")[1]

                        self.se.to_administrators(msg['request']['module_name'], msg['request']['user_uuid'], msg['channel'])

                        if action == "shutdown_now": # send to receiver to shutdown entire service
                            self.publish_message(message.channel, {"canary_breach": {"module_name": msg['request']['module_name'], "uuid": msg['request']['user_uuid'], "channel": ['channel'], "action": action}})
                            print("PolicyServer: Canary Breach level A, shutting down...")
                            os._exit(1)

                        elif action == "email_admins_blacklist":
                            self.pd.device_access_blacklist("*", "*", msg['request']['user_uuid'])

                else:
                    print("Not received expected parameters.")
                    # Receiver hasn't provided full information
                    # Maybe make this can be negligible for some parameters like module_name, as device_id should be enough
                    pass

            else:
                self.publish_message(message.channel, {"access": "granted", "channel": msg['channel'], "request": msg['request']})

    def publish_message(self, channel, message):
        response = json.loads(json.dumps(message))
        self.pubnub.publish().channel(channel).message(response).async(my_publish_callback)

if __name__ == "__main__":
    # temp - testing purposes only
    import gateway_database
    password = input("Database password: ")
    gdatabase = gateway_database.GatewayDatabase(host = 'ephesus.cs.cf.ac.uk', user = 'c1312433', password = password, database = 'c1312433')

    print(getattr(gdatabase, 'policy_key'))
    ps = PolicyServer(gdatabase)
