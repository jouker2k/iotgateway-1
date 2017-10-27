'''
__author__ = "@sgript"

Series of database calls for policy server to determine if access should be allowed, some maintenance functions to start policy server.
'''
import pymysql
import datetime
import time
from datetime import timedelta
from helpers.sha3 import sha3

class PolicyDatabase(object):
    def __init__(self, host, user, password, database):
        try:
            self.connection = pymysql.connect(host, user, password, database)
            print("PolicyDatabase: Connected.")

        except _mysql.Error as e:
            print("Error {}: {}".format(e.args[0], e.args[1]))
            sys.exit(1)

    def policy_key(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT auth_key_policy FROM gateway_keys")
        rows = cursor.fetchall()

        if len(rows) > 1:
            print("GatewayDatabaseWarning: There is more than one gateway receiver key set!")

        return rows[0][0]

    def pub_key(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT pub_key FROM gateway_keys")
        rows = cursor.fetchall()

        if len(rows) > 1:
            print("GatewayDatabaseWarning: There is more than one pub_key key set!")

        return rows[0][0]

    def sub_key(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT sub_key FROM gateway_keys")
        rows = cursor.fetchall()

        if len(rows) > 1:
            print("GatewayDatabaseWarning: There is more than one sub_key key set!")

        return rows[0][0]

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

    def delete_policy(self, policy_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM security_policy WHERE policy_id = '%s'" % (policy_id))

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

    def access_log(self, ip, user_uuid, channel_name, module_name, method_name, parameters, status):
        user_uuid = sha3(user_uuid)
        cursor = self.connection.cursor()
        parameters = str(parameters).replace("'", "''")
        date_time = time.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("INSERT INTO access_log(ip_address, date_time, user_uuid, channel_name, module_name, method_name, parameters, status) VALUES('%s', '%s','%s','%s','%s','%s','%s','%s');" % (ip, date_time, user_uuid, channel_name, module_name, method_name, parameters, status))

    def is_canary(self, canary_function):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT DISTINCT canary_function, canary_level FROM canary_functions WHERE canary_function = '%s';" % (canary_function))
        canary_exists = cursor.fetchall()

        if canary_exists:
            return [True, canary_exists[0][1]]
        else:
            return [False, ""]

    def canary_entry(self, file_name, function, canary_level, uuid = None):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO canary_functions(canary_module, canary_function, canary_level, uuid) VALUES('%s','%s', '%s','%s');" % (file_name, function, canary_level, uuid))

        print("GatewayDatabase: Canary file {} created at security level {}.".format(file_name, canary_level))

    def access_device(self, channel, mac_address, uuid, module_name, requested_function, parameters):
        hashed_uuid = sha3(uuid)

        cursor = self.connection.cursor()

        today = time.strftime('%Y-%m-%d') # Check if rejected 3 times today
        query = cursor.execute("SELECT date_time FROM access_log WHERE DATE(date_time) LIKE '%s' AND user_uuid = '%s' AND module_name = '%s' AND status LIKE  '%s'" % (today, hashed_uuid, module_name, "%" + "rejected" + "%"))
        rejected = cursor.fetchall()

        if len(rejected) >= 3:
            return [False, "today_over_rejected"]

        time_now = time.strftime('%H:%M:%S') # Check if last access rejected less than 1 minute ago
        query = cursor.execute("SELECT TIME(date_time) FROM access_log WHERE user_uuid = '%s' AND status LIKE '%s' ORDER  BY date_time DESC LIMIT 1;" % (hashed_uuid, "%" + "rejected" + "%"))
        last_access = cursor.fetchall()

        if last_access:
            t = datetime.datetime.now()
            time_now_delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            accessed_last = time_now_delta - last_access[0][0]
            if (accessed_last) < timedelta(minutes=1):
                return [False, "rejected_too_soon"]

        # Check things such as: if canary being accessed or if stolen channel
        query = cursor.execute("SELECT user_uuid FROM gateway_subscriptions WHERE channel = '%s' and user_uuid = '%s'" % (channel, hashed_uuid))
        valid_uuid_for_channel = cursor.fetchall()
        canary = self.is_canary(requested_function)
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
            self.device_access_blacklist("*", "", uuid)
            return [False, "invalid_uuid"]

        # Blacklist checks
        query = cursor.execute("SELECT user_uuid FROM device_access_blacklisted WHERE user_uuid = '%s' AND module_name = '%s' AND requested_function = '%s'" % (uuid, module_name, requested_function))
        blacklisted_specific = cursor.fetchall()

        if blacklisted_specific: # If blacklisted for this specific function for module
            print("PolicyDatabase: User {} blacklisted on {} function in {} module".format(uuid, requested_function, module_name))
            return [False, "blacklisted_specific"]

        else: # If blacklisted from all functions of a module
            query = cursor.execute("SELECT user_uuid FROM device_access_blacklisted WHERE user_uuid = '%s' AND module_name = '%s' AND requested_function '%s';" % (uuid, module_name, "*"))
            blacklisted_global_module = cursor.fetchall()

            if blacklisted_global_module:
                print("PolicyDatabase: User {} blacklisted globally on module {}".format(uuid, module_name))
                return [False, "blacklisted_global_module"]

            else: # If blacklisted from all modules
                query = cursor.execute("SELECT user_uuid FROM device_access_blacklisted WHERE user_uuid = '%s' OR module_name = '%s'" % (uuid, "*"))
                blacklisted_global = cursor.fetchall()

                if blacklisted_global:
                    print("PolicyDatabase: User {} blacklisted globally on all modules".format(uuid))
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

        t = datetime.datetime.now() # compare current time to time-frame from time policy
        now_delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        access = False
        if end_time <= start_time: # wrap around
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
