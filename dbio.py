import psycopg2
import time
from psycopg2._json import Json

'''
This class takes care of interacting with DB for storing/querying tweets
'''

class DBIO:
    cursor = None
    search_id = 0

    def __init__(self, config):
        self.init_db_connection(config)

    def init_db_connection(self, config):
        try:
            conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % \
                          (config.get('db', 'host'), config.get('db', 'dbname')
                          , config.get('db', 'user'), config.get('db', 'password'))

            # get a connection, if a connect cannot be made an exception will be raised here
            conn = psycopg2.connect(conn_string)
            conn.autocommit = True

            # conn.cursor will return a cursor object, you can use this cursor to perform queries
            self.cursor = conn.cursor()
            # print "Connected!\n"

        except Exception as e:
            print "Error: Could not establish database connection. \n" \
                  "Please make sure PostgreSQL is running and the connection parameters in keys.cnf file are correct."
            exit(1)

    def write_start_ts(self, search_mode, keywords):
        ts = time.strftime("%d%m%y")+time.strftime("%H%M%S")
        sql = "insert into tweets_metadb (start_time, search_mode, keywords) values (%s, %s, %s) RETURNING id;"
        self.cursor.execute(sql, (ts, search_mode, ','.join(["'"+str(i)+"'" for i in keywords])))
        self.search_id = self.cursor.fetchone()[0]

    def write_end_ts(self):
        ts = time.strftime("%d%m%y")+time.strftime("%H%M%S")
        sql = "update tweets_metadb set(end_time) = ("'%s'") where id=%s;"
        self.cursor.execute(sql, [ts, self.search_id])

    def write_tweet(self, tweet):
        job = Json(tweet)
        self.cursor.execute("insert into tweets_db (data, search_id) values (%s, %s)", [job, self.search_id])

    def query(self):
        self.cursor.execute("SELECT data->>'text', data#>>'{user,screen_name}' as User, data->>'id_str', id, search_id FROM tweets_db")

        for row in self.cursor:
            print str(row[4])+') '+str(row[3])+' : '+row[0]
            # url = "http://twitter.com/%s/status/%s" % (row[1], row[2])
            # print " -> " + url + '\n'  # Print tweet URL

    def get_search_id(self):
        return self.search_id