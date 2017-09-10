# pip install PyMySQLs
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
        row = cursor.execute("SELECT * FROM policy")
        rows = cursor.fetchall()

        print(rows)

    def access_device(self, device_id, module_name, user_uuid, state = None):
        cursor = self.connection.cursor()

        query_blacklist = cursor.execute("SELECT user_uuid FROM blacklist WHERE unique_id = '%s' AND user_uuid = '%s'" % (device_id, user_uuid))
        blacklisted = cursor.fetchall()

        if blacklisted:
            print("User is Blacklisted")
            return [False, "uuid_rejected"]

        print("User is not blacklisted")

        # if state exists we know will be single policy for a state + unique_id combination - fetch directly instead of for loop
        start_time = end_time = 0
        if state:
            state_type = state['state_type']
            state_value = state['state_value']

            query_allowed_time = cursor.execute("SELECT start_time, end_time FROM policy WHERE unique_id = '%s' AND state_type = '%s' AND state_value = '%s' AND module_name = '%s'" % (device_id, state_type, state_value, module_name))

            time_policy = cursor.fetchall()

            start_time = time_policy[0][1]
            end_time = time_policy[0][1]

        else:
            # TODO loop etc.
            pass

        t = datetime.datetime.now()
        delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

        if delta > start_time and delta < end_time:
            print("Time within range")
            return True

        else:
            print("Time not within range")
            return [False, "time_rejected"]

        print(delta > start_time)
        #print(now > start_time)

        #print(start_time, end_time)

if __name__ == "__main__":
    # TODO: Will accept input as this:
    # host = input("Host to connect to: ")
    # user - input("User to login as: ")
    password = input("Database password: ")
    # database = input("Database name: ")

    # temp
    host = 'ephesus.cs.cf.ac.uk'
    user = 'c1312433'

    database = 'c1312433'

    pd = PolicyDatabase(host, user, password, database)

    # temp
    pd.access_device('00:17:88:01:02:44:7a:d0-0b', 'philapi', 'test_user_uuid2', {"state_type": "on", "state_value": True})
