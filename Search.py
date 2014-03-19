import ConfigParser
import json
import pprint
from TwitterSearch import *
import psycopg2
import psycopg2.extras
from psycopg2._json import Json
import time
import sys
from tweepy import OAuthHandler, StreamListener, Stream


class GrepTwitter(StreamListener):

    SEARCH_MODE_ARCHIEVE = 'backward'
    SEARCH_MODE_STREAMING = 'forward'

    config = None
    cursor = None
    save_streaming_data = False
    streamin_tweets_count = 0
    streaming_tweets_list = []

    keywords = []
    search_mode = 0     # SEARCH API
    search_id = 0

    def __init__(self, search_mode, keywords):
        try:
            self.config = ConfigParser.ConfigParser()
            self.config.read("keys.cnf")
            self.keywords = keywords
            if search_mode == 'forward':
                self.search_mode = 1
            self.init_db_connection()
            self.write_start_ts()

            if self.search_mode == 0:
                self.search()
                self.write_end_ts()
            else:
                self.streaming_search()

            # self.query()
        except Exception as e:
            print(e)

    def init_db_connection(self):
        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % \
                          (self.config.get('db', 'host'), self.config.get('db', 'dbname')
                           , self.config.get('db', 'user'), self.config.get('db', 'password'))

        # print the connection string we will use to connect
        # print "Connecting to database\n	->%s" % conn_string

        # get a connection, if a connect cannot be made an exception will be raised here
        conn = psycopg2.connect(conn_string)
        conn.autocommit = True

        # conn.cursor will return a cursor object, you can use this cursor to perform queries
        self.cursor = conn.cursor()
        # print "Connected!\n"

    def search(self):
        try:

            tso = TwitterSearchOrder() # create a TwitterSearchOrder object
            tso.setKeywords(['stormireland']) # let's define all words we would like to have a look for
            tso.setLanguage('en') # we want to see German tweets only
            tso.setCount(7) # please dear Mr Twitter, only give us 7 results per page
            tso.setIncludeEntities(False) # and don't give us all those entity information

            # it's about time to create a TwitterSearch object with our secret tokens
            ts = TwitterSearch(
                consumer_key=self.config.get('twitter_keys', 'consumer_key'),
                consumer_secret=self.config.get('twitter_keys', 'consumer_secret'),
                access_token=self.config.get('twitter_keys', 'access_token'),
                access_token_secret=self.config.get('twitter_keys', 'access_token_secret')
            )

            for tweet in ts.searchTweetsIterable(tso):  # save to db
                job = Json(tweet)
                self.cursor.execute("insert into tweets_db (data, search_id) values (%s, %s)", [job, self.search_id])


            print 'done'
        except TwitterSearchException as e: # take care of all those ugly errors if there are some
            print(e)

    def streaming_search(self, save_to_db):
        self.save_streaming_data = save_to_db
        auth = OAuthHandler(self.config.get('twitter_keys', 'consumer_key'), self.config.get('twitter_keys', 'consumer_secret'))
        auth.set_access_token(self.config.get('twitter_keys', 'access_token'), self.config.get('twitter_keys', 'access_token_secret'))

        stream = Stream(auth, self)
        stream.filter(track=['indiawithmodi, rtept'])


    def query(self):
        self.cursor.execute("SELECT data->>'text', data#>>'{user,screen_name}' as User, data->>'id_str', id, search_id FROM tweets_db")

        for row in self.cursor:
            print str(row[4])+') '+str(row[3])+' : '+row[0]
            # url = "http://twitter.com/%s/status/%s" % (row[1], row[2])
            # print " -> " + url + '\n'  # Print tweet URL

    def write_start_ts(self):
        ts = time.strftime("%d%m%y")+time.strftime("%H%M%S")
        sql = "insert into tweets_metadb (start_time, search_mode, keywords) values (%s, %s, %s) RETURNING id;"
        self.cursor.execute(sql, (ts, self.search_mode, ','.join(["'"+str(i)+"'" for i in keywords])))
        self.search_id = self.cursor.fetchone()[0]

    def write_end_ts(self):
        ts = time.strftime("%d%m%y")+time.strftime("%H%M%S")
        sql = "update tweets_metadb set(end_time) = ("'%s'") where id=%s;"
        self.cursor.execute(sql, [ts, self.search_id])


    def on_data(self, data):
        print '%s : %s' % (self.save_streaming_data, data)
        tweet = json.loads(data, encoding='utf-8')
        self.streamin_tweets_count += 1
        self.streaming_tweets_list.append(tweet)

        if self.save_streaming_data:
            job = Json(tweet)
            self.cursor.execute("insert into tweets_db (data) values (%s)", [job])

        return True

    def on_error(self, status):
        print status

#keywords = ['stormireland']
#gt = GrepTwitter(keywords, GrepTwitter.SEARCH_MODE_ARCHIEVE)
# gt.init_db_connection()
# gt.streaming_search(False)
# gt.search(False)
# gt.query()

if __name__ == "__main__":
    keywords = sys.argv[2:]
    mode = sys.argv[1]

    gt = GrepTwitter(mode, keywords)
