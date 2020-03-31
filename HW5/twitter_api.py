import cred
from pymongo import Connection
import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import datetime


connection = Connection('localhost', 27017)
db = connection.TwitterStream
db.tweets.ensure_index("id", unique=True, dropDups=True)
collection = db.tweets

keywords = ['COVID-19','corona']
language = ['en']

class StdOutListener(StreamListener):

    def on_data(self, data):

        print(data)
        tweet_data = json.loads(data)

        tweet_id = tweet_data['id_str']
        username = tweet_data['user']['screen_name']
        text = tweet_data['text']
        hashtags = tweet_data['entities']['hashtags']
        dt = tweet_data['created_at']

        # created = datetime.datetime.strptime(dt, '%a %b %d %H:%M:%S +0000 %Y')

        tweet = {'id':tweet_id, 'username':username, 'text':text, 'hashtags':hashtags, 'created':dt}

        # Save the refined Tweet data to MongoDB
        collection.save(tweet)

        return True

    # Prints the reason for an error to your console
    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    listener = StdOutListener()
    auth = OAuthHandler(cred.consumer_key, cred.consumer_secret)
    auth.set_access_token(cred.access_token, cred.access_secret)

    stream = Stream(auth, listener)
    stream.filter(track=keywords, languages=language)
