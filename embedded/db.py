import pymysql

class DB(object):
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        try:
            self.connection = pymysql.connect(host, user, password, database)
            print("Database: Connected.")

        except _mysql.Error as e:
            print("DatabaseError {}: {}".format(e.args[0], e.args[1]))
            sys.exit(1)

    def embedded_devices_key(self):
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT embedded_devices_key FROM gateway_keys")
        rows = cursor.fetchall()

        if len(rows) > 1:
            print("GatewayDatabaseWarning: There is more than one gateway receiver key set!")

        return rows[0][0]


if __name__ == "__main__":

    password = input("Database password: ")
    # database = input("Database name: ")

    # temp
    host = 'ephesus.cs.cf.ac.uk'
    user = 'c1312433'

    database = 'c1312433'

    gd = DB(host, user, password, database)
    print(gd.set_receiver_auth_channel("test"))
    #print(gd.hide_canaries('platypus_0'))
#     gd.get_channels()
