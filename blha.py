import ConfigParser
from TwitterSearch import *

try:
    config = ConfigParser.ConfigParser()
    config.read("keys.cnf")

    tso = TwitterSearchOrder()
    tso.setCount(100)
    tso.setKeywords(['ireland'])

    ts = TwitterSearch(config.get('twitter_keys', 'consumer_key'), config.get('twitter_keys', 'consumer_secret'),
                       config.get('twitter_keys', 'access_token'),
                       config.get('twitter_keys', 'access_token_secret'))

    # init variables needed in loop
    todo = True
    next_max_id = 0

    # let's start the action
    while todo:

        # first query the Twitter API
        response = ts.searchTweets(tso)

        # print rate limiting status
        print "Current rate-limiting status: %s" % ts.getMetadata()['x-rate-limit-remaining']

        # check if there are statuses returned and whether we still have work to do
        todo = not len(response['content']['statuses']) == 0

        # check all tweets according to their ID
        for tweet in response['content']['statuses']:
            tweet_id = tweet['id']
            # print("Seen tweet with ID %i" % tweet_id)

            # current ID is lower than current next_max_id?
            if (tweet_id < next_max_id) or (next_max_id == 0):
                next_max_id = tweet_id
                next_max_id -= 1 # decrement to avoid seeing this tweet again

        # set lowest ID as MaxID
        tso.setMaxID(next_max_id)

except TwitterSearchException as e:
    print(e)