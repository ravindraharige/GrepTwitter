import ConfigParser
from TwitterSearch import *
import psycopg2
import psycopg2.extras
from psycopg2._json import Json


class GrepTwitter:

    config = None
    cursor = None

    def __init__(self):
        try:
            self.config = ConfigParser.ConfigParser()
            self.config.read("keys.cnf")
        except Exception as e:
            print(e)

    def initDBconnection(self):
        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % \
                          (self.config.get('db', 'host'), self.config.get('db', 'dbname')
                           , self.config.get('db', 'user'), self.config.get('db', 'password'))

        # print the connection string we will use to connect
        print "Connecting to database\n	->%s" % conn_string

        # get a connection, if a connect cannot be made an exception will be raised here
        conn = psycopg2.connect(conn_string)
        conn.autocommit = True

        # conn.cursor will return a cursor object, you can use this cursor to perform queries
        self.cursor = conn.cursor()
        print "Connected!\n"


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

            for tweet in ts.searchTweetsIterable(tso): # this is where the fun actually starts :)
                print('@%s tweeted: %s' % (tweet['user']['screen_name'], tweet['text']))
                job = Json(tweet)
                # cursor.execute("insert into tweets_db (data) values (%s)", [job])
                print tweet
                print '\n'

            print 'done'
        except TwitterSearchException as e: # take care of all those ugly errors if there are some
            print(e)

    def query(self):
        self.cursor.execute("SELECT data->>'text' FROM tweets_db")

        for row in self.cursor:
            data = row[0]
            print data

gt = GrepTwitter()
gt.initDBconnection()
gt.query()