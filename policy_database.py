import pymysql
import datetime
from datetime import timedelta
import time
from gateway_database import GatewayDatabase

'''
DB Columns?
===========
- module_name
- device_id
- start_time
- end_time
- blacklisted_user_uuid
'''

class PolicyDatabase(object):
    def __init__(self, host, user, password, database):
        try:
            self.connection = pymysql.connect(host, user, password, database)
            print("PolicyDatabase: Connected.")

        except _mysql.Error as e:
            print("Error {}: {}".format(e.args[0], e.args[1]))
            sys.exit(1)

    def get_policy(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT * FROM security_policy")
        rows = cursor.fetchall()
        return rows

    def set_policy(self, module_name, mac_address, requested_function, parameters, start_time, end_time):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO security_policy(module_name, mac_address, requested_function, parameters, start_time, end_time) VALUES('%s','%s','%s','%s','%s','%s');" % (module_name, mac_address, requested_function, parameters, start_time, end_time))

    def modify_policy(self, policy_id, start_time, end_time):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE security_policy SET start_time = '%s', end_time = '%s' WHERE policy_id = '%s';" % (start_time, end_time, policy_id))

    def get_blacklisted_auth(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT * FROM auth_blacklisted")
        rows = cursor.fetchall()
        return rows

    def get_device_blacklisted(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT * FROM device_access_blacklisted")
        rows = cursor.fetchall()
        return rows

    def undo_device_blacklist(self, uuid):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM device_access_blacklisted WHERE user_uuid = '%s'" % (uuid))

    def undo_auth_blacklist(self, uuid):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM auth_blacklisted WHERE user_uuid = '%s'" % (uuid))

    def device_access_blacklist(self, module_name, requested_function, user_uuid):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO device_access_blacklisted(module_name, requested_function, user_uuid) VALUES('%s','%s','%s');" % (module_name, requested_function, user_uuid))

    def access_log(self, user_uuid, channel_name, module_name, method_name, parameters, status):
        cursor = self.connection.cursor()
        parameters = str(parameters).replace("'", "''")
        date_time = time.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("INSERT INTO access_log(date_time, user_uuid, channel_name, module_name, method_name, parameters, status) VALUES('%s','%s','%s','%s','%s','%s','%s');" % (date_time, user_uuid, channel_name, module_name, method_name, parameters, status))

    def access_device(self, channel, mac_address, uuid, module_name, requested_function, parameters):
        cursor = self.connection.cursor()

        # Before anything first check if corresponding channel has correct UUID requesting:
        query = cursor.execute("SELECT user_uuid FROM gateway_subscriptions WHERE channel = '%s' and user_uuid = '%s'" % (channel, uuid))
        valid_uuid_for_channel = cursor.fetchall()

        if not valid_uuid_for_channel:
            print("The UUID {} is not a valid subscriber for the channel {}, blacklisting...".format(uuid, channel))
            self.device_access_blacklist(module_name, requested_function, uuid)
            return [False, "invalid_uuid"]

        # Check if user blacklisted for those functions/modules
        query = cursor.execute("SELECT user_uuid FROM device_access_blacklisted WHERE user_uuid = '%s' AND module_name = '%s' AND requested_function = '%s'" % (uuid, module_name, requested_function))
        blacklisted = cursor.fetchall()

        if blacklisted:
            print("PolicyDatabase: User {} blacklisted on {} function in {} module".format(uuid, requested_function, module_name))
            return [False, "blacklisted"]

        # Check if device access time policy is accepted
        start_time = end_time = datetime.timedelta(hours=0)
        if requested_function:
            parameters = str(parameters).replace("'", "''")

            query_allowed_time = cursor.execute("SELECT `start_time`, `end_time` FROM `security_policy` WHERE mac_address = '%s' AND requested_function = '%s' AND parameters = '%s' AND module_name = '%s'" % (mac_address, requested_function, parameters, module_name))

            time_policy = cursor.fetchall()

            if query_allowed_time != 0:
                start_time = time_policy[0][0]
                end_time = time_policy[0][1]
            else:
                print("PolicyDatabase: Time policy not specified for {} function on {} module requested by user: {}".format(requested_function, module_name, uuid))
                return [False, "time_rejected"]

        t = datetime.datetime.now()
        time = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        access = False
        if end_time <= start_time:
            access = start_time <= time or end_time >= time
        else:
            access = start_time <= time <= end_time

        print("Timeframe for {} function on {} module: {}–{}".format(requested_function, module_name, start_time, end_time))
        if access:
            print("PolicyDatabase: Time within range for {} function on {} module requested by user: {}".format(requested_function, module_name, uuid))
            return [access, "time_granted"]

        else:
            print("PolicyDatabase: Time not within range {} function on {} module requested by user: {}".format(requested_function, module_name, uuid))
            return [access, "time_rejected"]

# if __name__ == "__main__":
#     password = input("Database password: ")
#     host = 'ephesus.cs.cf.ac.uk'
#     user = 'c1312433'
#     database = 'c1312433'
#
#     pd = PolicyDatabase(host, user, password, database)
#     # temp riieiw934w9291o3992sk
#     pd.access_device('ALF0OCK6IC', '00:17:88:6c:d6:d3', 'platypus_0', 'philapi', 'light_switch', [False, 1])
#     # pd.undo_device_blacklist('test_user_uuid_2')
#     # pd.set_policy('philapi', '00:17:88:6c:d6:d3', 'show_hues', '', '06:00', '05:59')
#
#     #pd.modify_policy(1, '00:23:00', '00:03:00')
