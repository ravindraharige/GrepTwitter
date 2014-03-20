import ConfigParser
import json
import sys

from TwitterSearch import *
from tweepy import OAuthHandler, StreamListener, Stream

from dbio import DBIO


class GrepTwitter(StreamListener):
    SEARCH_MODE_ARCHIEVE = 0
    SEARCH_MODE_STREAMING = 1

    config = None

    keywords = []
    search_mode = SEARCH_MODE_ARCHIEVE     # SEARCH API

    io = None

    def __init__(self, search_mode, keys):
        try:
            self.config = ConfigParser.ConfigParser()
            self.config.read("keys.cnf")
            self.keywords = keys
            if search_mode == 'forward':
                self.search_mode = 1

            self.io = DBIO(self.config)
            self.io.write_start_ts(self.search_mode, keywords)

            if self.search_mode == self.SEARCH_MODE_ARCHIEVE:
                self.search()
                self.io.write_end_ts()
            else:
                self.streaming_search()

                # self.query()
        except Exception as e:
            print(e)

    def search(self):
        done = False
        try:

            tso = TwitterSearchOrder()  # create a TwitterSearchOrder object
            tso.setKeywords(self.keywords)  # let's define all words we would like to have a look for
            tso.setLanguage('en')  # we want to see English tweets only
            tso.setCount(100)  # give 7 results per page
            tso.setIncludeEntities(False)  # and don't give us all those entity information
            tso.setGeocode(53.3333328, -8.0, 300, True)
            tso.url
            # it's about time to create a TwitterSearch object with our secret tokens
            ts = TwitterSearch(
                consumer_key=self.config.get('twitter_keys', 'consumer_key'),
                consumer_secret=self.config.get('twitter_keys', 'consumer_secret'),
                access_token=self.config.get('twitter_keys', 'access_token'),
                access_token_secret=self.config.get('twitter_keys', 'access_token_secret')
            )

            count = 0
            for tweet in ts.searchTweetsIterable(tso):  # save to db
                count += 1
                self.io.write_tweet(tweet)

            print 'Search complete.. flushed %d tweets into db.'%count
        except TwitterSearchException as e:  # take care of all those ugly errors if there are some
            print 'haha'
            print(e)

    def streaming_search(self):
        auth = OAuthHandler(self.config.get('twitter_keys', 'consumer_key'),
                            self.config.get('twitter_keys', 'consumer_secret'))
        auth.set_access_token(self.config.get('twitter_keys', 'access_token'),
                              self.config.get('twitter_keys', 'access_token_secret'))

        stream = Stream(auth, self)
        stream.filter(track=['indiawithmodi, rtept'])

    def on_data(self, data):
        print '%s: ' % data
        tweet = json.loads(data, encoding='utf-8')

        save = False
        if save is True:
            self.io.write_tweet(tweet)

        return True

    def on_error(self, status):
        print status


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print 'Error: Not sufficient parameters. \n' \
              'Usage: python search.py <mode:forward|backward> <keyword1, keyword2..>'
        exit(0)

    keywords = sys.argv[2:]
    mode = sys.argv[1]
    print mode
    print keywords
    gt = GrepTwitter(mode, keywords)
