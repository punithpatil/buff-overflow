import cred
from pymongo import MongoClient
import json
import requests
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import datetime

keywords = ['covid19','ncov','corona','coronavirus','covid2019']
language = ['en']

def create_mongo_connection():
    connection = MongoClient('localhost', 27017)
    db = connection.TwitterStream
    db.tweets.ensure_index("id", unique=True, dropDups=True)
    collection = db.tweets
    return collection

def print_coordinates(coordinates):
    print(coordinates)

class StdOutListener(StreamListener):
    def __init__(self, collection):
        self.collection = collection

    def on_data(self, data):
        tweet_data = json.loads(data)

        try:
            place=tweet_data['place']
            if place!=None:
                coordinates = place['bounding_box']['coordinates']
                longt = coordinates[0][0][0]
                lat = coordinates[0][0][1]
                tweet = {'Latitude':lat,'Longitude':longt,'hashtags':tweet_data['entities']['hashtags'],'username':tweet_data['user']['screen_name']}                               
                #print(coordinates)
                self.collection.save(tweet)

        except KeyError:
            print_coordinates("\n")

        return True

    # Prints the reason for an error to your console
    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    listener = StdOutListener(create_mongo_connection())
    auth = OAuthHandler(cred.consumer_key, cred.consumer_secret)
    auth.set_access_token(cred.access_token, cred.access_secret)

    stream = Stream(auth, listener)
    stream.filter(track=keywords, languages=language)

