
import json
import policy_database

from pubnub.enums import PNStatusCategory
from pubnub.callbacks import SubscribeCallback
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy

def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];


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

        # REVIEW: This needs to be done automatically via PolicyDatabase (w/o constructor params) + done via fetching credentials remotely or typed
        self.pd = policy_database.PolicyDatabase(gdatabase.host, gdatabase.user, gdatabase.password, gdatabase.database)

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

        if 'access' not in msg:
            if msg['request']['module_name'] != 'help':
                if 'user_uuid' in msg['request'] and 'mac_address' in msg:

                    access = self.pd.access_device(msg['channel'], msg['mac_address'], msg['request']['user_uuid'], msg['request']['module_name'], msg['request']['requested_function'], msg['request']['parameters'])[0]

                    status = "granted" if access is True else "rejected"

                    self.publish_message(message.channel, {"access": status, "channel": msg['channel'], "request": msg['request']})
                    self.pd.access_log(msg['request']['user_uuid'], msg['channel'], msg['request']['module_name'], msg['request']['requested_function'], msg['request']['parameters'], status)

                    print("PolicyServer: Access on {} by {} logged as {}".format(msg['channel'], msg['request']['user_uuid'], status))

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

# if __name__ == "__main__":
#     ps = PolicyServer()
