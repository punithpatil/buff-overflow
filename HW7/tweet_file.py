import os
import sys
import re
import cred
from pymongo import MongoClient
import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from datetime import datetime
from dateutil import parser
import pandas as pd
import matplotlib.pyplot as plt

connection = MongoClient('localhost', 27017)
keywords = ['covid19', 'ncov', 'corona', 'coronavirus', 'covid2019']
language = ['en']
colq = connection.db.tweets_sfe
coll1 = connection.db.tweets_sample


class StdOutListener(StreamListener):
    def on_data(self, data):
        tweet_data = json.loads(data)
        # print(tweet_data)
        try:
            place = tweet_data['place']
            if place != None:
                coordinates = place['bounding_box']['coordinates']
                longt = coordinates[0][0][0]
                lat = coordinates[0][0][1]
                user_location = tweet_data['user']['location']
                user_likes = tweet_data['user']['favourites_count']
                retweet_info = tweet_data['retweet_count']
                tweet_text = tweet_data['text']
                created_date = parser.parse(
                    tweet_data['created_at'], ignoretz=True)
                date_tweet = {'Created_date': created_date,
                              'Likes': user_likes, 'Timezone': tweet_data['user']['time_zone']}
                tweet = {'Latitude': lat, 'Longitude': longt,
                         'hashtags': tweet_data['entities']['hashtags'], 'username': tweet_data['user']['screen_name'],
                         'Created_date': created_date, 'Location': user_location, 'Tweet_text': tweet_text,
                         'Likes': user_likes, 'Timezone': tweet_data['user']['time_zone']}
                print(tweet)
                colq.insert_one(tweet)
                coll1.insert_one(date_tweet)
                tweet_cursor = colq.find()
                tweet_sample_cursor = coll1.find()
                df = pd.DataFrame(list(tweet_cursor))
                df = df.sort_values(by='Likes', ascending=False)
                df = df.reset_index(drop=True)
                if len(df) > 5:
                    for j in range(5):
                        print(df.iloc[j, 8])
                        print('\n')
                df['Created_date'] = pd.to_datetime(df['Created_date'])
                df_final = df.groupby(
                    [pd.Grouper(key='Created_date', freq='H')]).size().reset_index(name='count')

                df2 = pd.DataFrame(list(tweet_sample_cursor))
                print(df_final.columns)
                df_final.plot(x='Created_date',
                              y='count', kind='line', c='r')
                plt.show()
                plt.savefig(
                    '/home/ec2-user/BuffOverflow/static/plotimage.png')

                print(df_final.tail())

        except KeyError:
            print('KeyError')

        return True

    def on_error(self, status):
        print(status)


if __name__ == '__main__':
    listener = StdOutListener()
    auth = OAuthHandler(cred.consumer_key, cred.consumer_secret)
    auth.set_access_token(cred.access_token, cred.access_secret)
    stream = Stream(auth, listener)
    stream.filter(track=keywords, languages=language)
