import ConfigParser
import pprint
from TwitterSearch import *
import psycopg2
import psycopg2.extras
from psycopg2._json import Json


try:
    config = ConfigParser.ConfigParser()
    config.read("keys.cnf")

    conn_string = "host='localhost' dbname='rte' user='ravo' password='rtepass'"

    # print the connection string we will use to connect
    print "Connecting to database\n	->%s" % (conn_string)

    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)
    psycopg2.extras.register_json(conn)

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()
    print "Connected!\n"

    tso = TwitterSearchOrder() # create a TwitterSearchOrder object
    tso.setKeywords(['stormireland']) # let's define all words we would like to have a look for
    tso.setLanguage('en') # we want to see German tweets only
    tso.setCount(7) # please dear Mr Twitter, only give us 7 results per page
    tso.setIncludeEntities(False) # and don't give us all those entity information

    # it's about time to create a TwitterSearch object with our secret tokens
    ts = TwitterSearch(
        consumer_key=config.get('twitter_keys', 'consumer_key'),
        consumer_secret=config.get('twitter_keys', 'consumer_secret'),
        access_token=config.get('twitter_keys', 'access_token'),
        access_token_secret=config.get('twitter_keys', 'access_token_secret')
    )

    for tweet in ts.searchTweetsIterable(tso): # this is where the fun actually starts :)
        print( '@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text'] ) )
        print('%r', type(tweet))
        # print '%r', json.dumps(tweet, ensure_ascii=False, sort_keys=True, indent=4).encode('utf8')
        # job = json.dumps(tweet)
        job = Json(tweet)
        pprint.pprint(job)
        # cursor.execute("insert into tweets_db (data) values (%s)", [job])

        print '\n'

    conn.commit()
    print 'done'
except TwitterSearchException as e: # take care of all those ugly errors if there are some
    print(e)
