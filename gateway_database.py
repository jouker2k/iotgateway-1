import pymysql

class GatewayDatabase(object):
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        try:
            self.connection = pymysql.connect(host, user, password, database)
            print("GatewayDatabase: Connected.")

        except _mysql.Error as e:
            print("GatewayDatabaseError {}: {}".format(e.args[0], e.args[1]))
            sys.exit(1)

    def receivers_key(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT auth_key_receiver FROM gateway_keys")
        rows = cursor.fetchall()

        if len(rows) > 1:
            print("GatewayDatabaseWarning: There is more than one gateway receiver key set!")

        return rows[0][0]

    def get_uuid_from_channel(self, channel):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT user_uuid FROM gateway_subscriptions WHERE channel = '%s';" % (channel))
        rows = cursor.fetchall()

        if rows:
            return rows[0][0]

    def hide_canaries(self, uuid):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT DISTINCT canary_function FROM canary_functions WHERE uuid != '%s' AND uuid != '%s' AND uuid IS NOT NULL;" % (uuid, None))
        rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append(row[0])

        print(result)
        return result

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

    def auth_blacklist(self, channel_name, uuid): # TODO: Move directly to Policy server?
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO auth_blacklisted(channel, user_uuid) VALUES('%s','%s');" % (channel_name, uuid))

        print("GatewayDatabase: UUID {} blacklisted due to violation on {} channel".format(uuid, channel_name))

    def gateway_subscriptions(self, channel_name, uuid):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO gateway_subscriptions(channel, user_uuid) VALUES('%s','%s');" % (channel_name, uuid))

        print("GatewayDatabase: New subscription added to channel {} containing user {}".format(channel_name, uuid))

    def gateway_subscriptions_remove(self, channel_name, uuid):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM gateway_subscriptions WHERE channel = '%s' AND user_uuid = '%s'" % (channel_name, uuid))

        print("GatewayDatabase: Subscription on channel {} containing user {} deleted.".format(channel_name, uuid))

    def get_channels(self):
        cursor = self.connection.cursor()
        query = cursor.execute("SELECT channel FROM gateway_subscriptions")

        rows = cursor.fetchall()
        subscription_channels = [i[0] for i in rows]

        return subscription_channels

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
#     print(gd.hide_canaries('platypus_0'))
# #     gd.get_channels()
