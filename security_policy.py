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
- blacklisted_uuid
'''

class PolicyDatabase(object):
    def __init__(self, host, user, password, database):
        try:
            self.connection = pymysql.connect(host, user, password, database)

        except _mysql.Error as e:
            print("Error {}: {}".format(e.args[0], e.args[1]))
            sys.exit(1)

#def db_connect(hot, user, password, db):
    def get_policy(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT * FROM policy")
        rows = cursor.fetchall()

        print(rows)

    def access_device(self, device_id, module_name, uuid, state = None):
        cursor = self.connection.cursor()
        #date = cursor.execute("SELECT policy.unique_id, blacklist.user_uuid, policy.start_time, policy.end_time FROM policy INNER JOIN blacklist WHERE policy.unique_id = '%s'" % (device_id))
        query_allowed_time = cursor.execute("SELECT start_time, end_time FROM policy WHERE unique_id = '%s' AND state = '%s'" % (device_id, state))
        rows = cursor.fetchall()

        # if state exists we know will be single policy for a state + unique_id combination - fetch directly instead of for loop
        start_time = end_time = 0
        if state:
            start_time = rows[0][1]
            end_time = rows[0][1]

        else:
            # TODO loop etc.
            pass

        t = datetime.datetime.now()
        delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

        print(delta, start_time)

        if delta > start_time and delta < end_time:
            return True

        else:
            return False

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
    pd.access_device('00:17:88:01:02:44:7a:d0-0b', 'philapi', 'test_uuid', 'on')
