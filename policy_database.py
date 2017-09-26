import pymysql
import datetime
from datetime import timedelta
import time

'''
DB Columns?
===========
- module_name
- device_id
- start_time
- end_time
- blacklisted_user_uuid
'''

# TODO Perhaps allow creating Canary from here, so we make canary_entry() from here (see GatewayDatabase) then it sends msg to receiver to fulfil the canary?
# Perhaps even send python code in a pastebin link to parse and save as a file – fully remote.

class PolicyDatabase(object):
    def __init__(self, host, user, password, database):
        try:
            self.connection = pymysql.connect(host, user, password, database)
            print("PolicyDatabase: Connected.")

        except _mysql.Error as e:
            print("Error {}: {}".format(e.args[0], e.args[1]))
            sys.exit(1)

    def get_admin_emails(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT * FROM administrator_emails")
        rows = cursor.fetchall()
        return rows

    def get_email_config(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT * FROM email_config")
        rows = cursor.fetchall()
        return rows

    def get_policy(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT * FROM security_policy")
        rows = cursor.fetchall()
        return rows

    def set_policy(self, module_name, mac_address, requested_function, parameters, start_time, end_time):
        parameters = ", ".join(map(str, parameters))
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

    def is_canary(self, canary_name):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT DISTINCT canary_function, canary_level FROM canary_functions WHERE canary_function = '%s';" % (canary_name))
        canary_exists = cursor.fetchall()

        if canary_exists:
            return [True, canary_exists[0][1]]
        else:
            return [False, ""]

    def canary_entry(self, file_name, canary_level, uuid = None):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO canary_functions(canary_function, canary_level, uuid) VALUES('%s','%s', '%s');" % (file_name, canary_level, uuid))

        print("GatewayDatabase: Canary file {} created at security level {}.".format(file_name, canary_level))

    def access_device(self, channel, mac_address, uuid, module_name, requested_function, parameters):
        cursor = self.connection.cursor()

        today = time.strftime('%Y-%m-%d')
        query = cursor.execute("SELECT date_time FROM access_log WHERE DATE(date_time) LIKE '%s' AND (user_uuid = '%s' OR channel_name = '%s') AND module_name = '%s' AND status LIKE '%s'" % (today, uuid, channel, module_name, "rejected"))
        rejected = cursor.fetchall()

        if len(rejected) >= 3:
            return [False, "today_over_rejected"]

        time_now = time.strftime('%H:%M:%S')
        query = cursor.execute("SELECT TIME(date_time) FROM access_log WHERE user_uuid = '%s' OR channel_name = '%s' AND status LIKE '%s' ORDER  BY date_time DESC LIMIT 1;" % (uuid, channel, "rejected"))
        last_access = cursor.fetchall()

        if last_access:
            t = datetime.datetime.now()
            time_now_delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            accessed_last = time_now_delta - last_access[0][0]
            if (accessed_last) < timedelta(minutes=1):
                return [False, "rejected_too_soon"]
            else:
                 print("PolicyDatabase: Last access: {}".format(accessed_last))

        # Before anything first check if corresponding channel has correct UUID requesting:
        query = cursor.execute("SELECT user_uuid FROM gateway_subscriptions WHERE channel = '%s' and user_uuid = '%s'" % (channel, uuid))
        valid_uuid_for_channel = cursor.fetchall()
        canary = self.is_canary(module_name)
        canary_breach_level = canary[1]

        if canary[0]:
            if canary_breach_level == "A":
                return [False, "canary_breach:shutdown_now"]

            elif canary_breach_level == "B":
                return [False, "canary_breach:email_admins_blacklist"]

            elif canary_breach_level == "C":
                return [False, "canary_breach:email"]

        if not valid_uuid_for_channel:
            print("The UUID {} is not a valid subscriber for the channel {}, blacklisting...".format(uuid, channel))
            self.device_access_blacklist(module_name, requested_function, uuid)
            return [False, "invalid_uuid"]

        # Check if user blacklisted for those functions/modules
        query = cursor.execute("SELECT user_uuid FROM device_access_blacklisted WHERE user_uuid = '%s' AND module_name = '%s' AND requested_function = '%s'" % (uuid, module_name, requested_function))
        blacklisted_specific = cursor.fetchall()

        if blacklisted_specific:
            print("PolicyDatabase: User {} blacklisted on {} function in {} module".format(uuid, requested_function, module_name))
            return [False, "blacklisted_specific"]

        else:
            # query = cursor.execute("SELECT devbl.user_uuid, abl.user_uuid FROM device_access_blacklisted AS devbl, auth_blacklisted AS abl WHERE (devbl.user_uuid = '%s' AND devbl.module_name = '%s') OR (abl.user_uuid = '%s' OR abl.channel = '%s')" % (uuid, "*", uuid, channel))
            # blacklisted_global_module = cursor.fetchall()
            query = cursor.execute("SELECT user_uuid FROM device_access_blacklisted WHERE user_uuid = '%s' AND module_name = '%s';" % (uuid, "*"))
            blacklisted_global_module = cursor.fetchall()

            if blacklisted_global_module:
                print("PolicyDatabase: User {} blacklisted globally on module {}".format(uuid, module_name))
                return [False, "blacklisted_global_module"]

            else:
                query = cursor.execute("SELECT user_uuid FROM auth_blacklisted WHERE user_uuid = '%s' OR channel = '%s'" % (uuid, channel))
                blacklisted_global = cursor.fetchall()

                if blacklisted_global:
                    print("PolicyDatabase: User {} blacklisted globally".format(uuid))
                    return [False, "blacklisted_global"]

        # Check if device access time policy is accepted
        start_time = end_time = datetime.timedelta(hours=0)
        if requested_function:
            parameters = ", ".join(map(str, parameters))

            query_allowed_time = cursor.execute("SELECT `start_time`, `end_time` FROM `security_policy` WHERE mac_address = '%s' AND requested_function = '%s' AND parameters = '%s' AND module_name = '%s'" % (mac_address, requested_function, parameters, module_name))
            time_policy = cursor.fetchall()

            if query_allowed_time != 0:
                start_time = time_policy[0][0]
                end_time = time_policy[0][1]
            else:
                print("PolicyDatabase: Time policy not specified for {} function on {} module requested by user: {}".format(requested_function, module_name, uuid))
                return [False, "time_rejected"]

        t = datetime.datetime.now()
        now_delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        access = False
        if end_time <= start_time:
            access = start_time <= now_delta or end_time >= now_delta
        else:
            access = start_time <= now_delta <= end_time

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
#     # print(pd.access_device('ALF0OCK6IC', '0', 'platypus_0', 'smart_things', 'toggle_switch', ["Hue white lamp 1"]))
#     print(pd.access_device('KBKAMUKDZ1', '00:17:88:6c:d6:d3', 'platypus_194', 'philapi', 'light_switch', [False, 1]))
#     #pd.is_canary("file_read")
#     # pd.undo_device_blacklist('test_user_uuid_2')
#     # pd.set_policy('philapi', '00:17:88:6c:d6:d3', 'show_hues', '', '06:00', '05:59')
#
#     #pd.modify_policy(1, '00:23:00', '00:03:00')
