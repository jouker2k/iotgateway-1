'''
__author__ = "@sgript"

Policy server, handles communication to grant access / instruct gateway, used for remotely modifying/adding/deleting policies also
'''
import json, ast
import policy_database
import sys, os
import send_email

from pubnub.enums import PNStatusCategory
from pubnub.callbacks import SubscribeCallback
from helpers.callbacks import my_publish_callback
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy

class PolicyServer(SubscribeCallback):

    def __init__(self, host, user, password, database):
        self.pd = policy_database.PolicyDatabase(host, user, password, database)

        self.pnconfig = PNConfiguration()
        self.pnconfig.uuid = 'GP'
        self.pnconfig.subscribe_key = self.pd.sub_key()
        self.pnconfig.publish_key = self.pd.pub_key()
        self.pnconfig.cipher_key = self.pd.get_cipher_key()
        self.pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
        self.pnconfig.ssl = True
        self.pnconfig.subscribe_timeout = self.pnconfig.connect_timeout = self.pnconfig.non_subscribe_timeout = 9^99

        self.pnconfig.auth_key = self.pd.policy_key() # later store elsewhere
        self.pubnub = PubNub(self.pnconfig)

        self.pubnub.add_listener(self)
        self.pubnub.subscribe().channels('policy').execute()

        self.se = send_email.Alert(self.pd)

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
        if 'policy_admin' in msg.keys():
            print(msg['policy_admin']['requested_function'])
            method_to_call = getattr(self.pd, msg['policy_admin']['requested_function'])
            result = method_to_call(*msg['policy_admin']['parameters']) # call requested function

            if method_to_call != getattr(self.pd, "canary_entry"): # if not remoteely creating canary, it was remote policy controls, show result
                if result is not None:
                    self.publish_message(message.channel, {"result.policy.admin": result})
                else:
                    self.publish_message(message.channel, {"result.policy.admin": "successully ran {}".format(msg['policy_admin']['requested_function'])})

            else: # if remote canary instruct gateway to make a file
                self.publish_message('policy', {"canary": msg['policy_admin']})

        # Otherwise is a regular access request from user sent to gateway
        # gateway has sent it here to check if policy will allow it
        elif 'request' in msg.keys():
            if msg['request']['module_name'] != 'help':
                if 'user_uuid' in msg['request'] and 'mac_address' in msg:

                    # check with database to confirm if access is possible
                    access = self.pd.access_device(msg['channel'], msg['mac_address'], msg['request']['user_uuid'], msg['request']['module_name'], msg['request']['requested_function'], msg['request']['parameters'])

                    status = "granted" if access[0] is True else "rejected: {}".format(access[1])

                    self.publish_message(message.channel, {"access": status, "channel": msg['channel'], "request": msg['request']})
                    self.pd.access_log(msg['request']['user_uuid'], msg['channel'], msg['request']['module_name'], msg['request']['requested_function'], msg['request']['parameters'], status)

                    print("PolicyServer: Access on {} by {} logged as {}".format(msg['channel'], msg['request']['user_uuid'], status))

                    if "canary_breach" in access[1]: # if requested function was canary,
                        action = access[1].split(":")[1]

                        # always send admins an email
                        self.se.to_administrators(msg['request']['module_name'], msg['request']['requested_function'], msg['request']['user_uuid'], msg['channel'])

                        if action == "shutdown_now": # if severity causes shutdown, tell gateway to shutdown too
                            self.publish_message(message.channel, {"canary_breach": {"module_name": msg['request']['module_name'], "uuid": msg['request']['user_uuid'], "channel": ['channel'], "action": action}})
                            print("PolicyServer: Canary Breach level A, shutting down...")
                            os._exit(1)

                        elif action == "email_admins_blacklist": # if severity causes blacklist, blacklist user entirely from all modules
                            self.pd.device_access_blacklist("*", "", msg['request']['user_uuid'])

                elif 'user_uuid' not in msg['request']:
                    self.publish_message(message.channel, {"error": "must provide user uuid", "channel": msg['channel']})

            else:
                self.publish_message(message.channel, {"access": "granted", "channel": msg['channel'], "request": msg['request']})

    def publish_message(self, channel, message):
        response = json.loads(json.dumps(message))
        self.pubnub.publish().channel(channel).message(response).async(my_publish_callback)

if __name__ == "__main__":
    host = 'ephesus.cs.cf.ac.uk'
    user = 'c1312433'
    password = input("Database password: ")
    database = 'c1312433'

    ps = PolicyServer(host, user, password, database)
