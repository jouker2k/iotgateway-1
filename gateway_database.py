import pymysql


class GatewayDatabase(object):
    def __init__(self, host, user, password, database):

        try:
            self.connection = pymysql.connect(host, user, password, database)
            print("GatewayDatabase: Connected.")

        except _mysql.Error as e:
            print("GatewayDatabaseError {}: {}".format(e.args[0], e.args[1]))
            sys.exit(1)

        # TODO: n startup need to re-subscribe to all the keys.


    def receivers_key(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT auth_key_receiver FROM gateway_keys")
        rows = cursor.fetchall()

        if len(rows) > 1:
            print("GatewayDatabaseWarning: There is more than one gateway receiver key set!")

        return rows[0][0]

    def policy_key(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT auth_key_policy FROM gateway_keys")
        rows = cursor.fetchall()

        if len(rows) > 1:
            print("GatewayDatabaseWarning: There is more than one gateway receiver key set!")

        return rows[0][0]


    def sec_key(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT sec_key FROM gateway_keys")
        rows = cursor.fetchall()

        if len(rows) > 1:
            print("GatewayDatabaseWarning: There is more than one secret_key key set!")

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

    def auth_blacklist(self, channel_name, uuid):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO auth_blacklisted(channel, user_uuid) VALUES('%s','%s');" % (channel_name, uuid))

        print("GatewayDatabase: UUID {} blacklisted due to violation on {} channel".format(uuid, channel_name))

    def gateway_subscriptions(self, channel_name, uuid):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO gateway_subscriptions(channel, user_uuid) VALUES('%s','%s');" % (channel_name, uuid))

        print("GatewayDatabase: New subscription added to channel {} containing user {}".format(channel_name, uuid))

# if __name__ == "__main__":
#
#     password = input("Database password: ")
#     # database = input("Database name: ")
#
#     # temp
#     host = 'ephesus.cs.cf.ac.uk'
#     user = 'c1312433'
#
#     database = 'c1312433'
#
#     gd = GatewayDatabase(host, user, password, database)
#
#     # temp
#     print("Receivers key: {}".format(gd.receivers_key()))
#     print("Policy key: {}".format(gd.policy_key()))
#     print("Secret key: {}".format(gd.sec_key()))
#     print("Sub key: {}".format(gd.sub_key()))
#     print("Pub key: {}".format(gd.pub_key()))
