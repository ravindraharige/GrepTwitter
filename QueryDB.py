import psycopg2
import psycopg2.extras


def main():
    #Define our connection string
    conn_string = "host='localhost' dbname='rte' user='ravo' password='rtepass'"

    # print the connection string we will use to connect
    print "Connecting to database\n	->%s" % (conn_string)

    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    # cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor = conn.cursor()



    print "Connected!\n"

    cursor.execute("SELECT data->>'text' FROM tweets_db")
    # records = cursor.fetchall()
    # pprint.pprint(records)

    # res = [json.dumps(dict(record)) for record in cursor]

    for row in cursor:
        data = row[0]
        print data

if __name__ == "__main__":
    main()
