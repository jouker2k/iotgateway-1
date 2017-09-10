
import json
import policy_database

from pubnub.enums import PNStatusCategory
from pubnub.callbacks import SubscribeCallback
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration, PNReconnectionPolicy

pnconfig = PNConfiguration()

pnconfig.subscribe_key = 'demo'
pnconfig.publish_key = 'demo'

pubnub = PubNub(pnconfig)


def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];


class PolicyServer(SubscribeCallback):

    def __init__(self):
        self.pnconfig = PNConfiguration()
        self.pnconfig.uuid = 'policy'
        self.pnconfig.subscribe_key = 'sub-c-12c2dd92-860f-11e7-8979-5e3a640e5579'
        self.pnconfig.publish_key = 'pub-c-85d5e576-5d92-48b0-af83-b47a7f21739f'
        self.pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
        self.pnconfig.ssl = True
        self.pnconfig.subscribe_timeout = self.pnconfig.connect_timeout = self.pnconfig.non_subscribe_timeout = 9^99

        self.pnconfig.auth_key = 'policy_key' # later store elsewhere
        self.pubnub = PubNub(self.pnconfig)

        self.pubnub.add_listener(self)
        self.pubnub.subscribe().channels('policy').execute()

        # REVIEW: This needs to be done automatically via PolicyDatabase (w/o constructor params) + done via fetching credentials remotely or typed
        self.pd = policy_database.PolicyDatabase("ephesus.cs.cf.ac.uk", "c1312433", "berlin", "c1312433")

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
        expected_parameters = ['device_id', 'module_name', 'user_uuid', 'state']

        if all(x in msg for x in expected_parameters):
            access = self.pd.access_device(msg['device_id'], msg['module_name'], msg['user_uuid'], msg['state'])
            print("access: {}".format(access))
            if access is True:
                self.publish_message(message.channel, '{"status": 1, "type": None}') # will make up codes for granted/time_rejected/uuid_rejected

            else:
                self.publish_message(message.channel, {"status": 2, "type": access[1]})

        else:
            print("Not received expected parameters.")
            # Receiver hasn't provided full information
            # Maybe make this can be negligible for some parameters like module_name, as device_id should be enough
            pass


        pass  # Handle new message stored in message.message

    def publish_message(self, channel, message):
        response = json.loads(json.dumps(message))
        print(channel)
        self.pubnub.publish().channel(channel).message(response).async(my_publish_callback)

if __name__ == "__main__":
    ps = PolicyServer()
