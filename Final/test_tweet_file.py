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
from nltk.tokenize import TweetTokenizer
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from wordcloud import WordCloud

connection = MongoClient('localhost', 27017)
keywords = ['covid19', 'ncov', 'corona', 'coronavirus', 'covid2019']
language = ['en']
colq = connection.db.tweets_sfe


def Prepare_Tweet(tweet_data):
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
        tweet = {'Latitude': lat, 'Longitude': longt,
                 'hashtags': tweet_data['entities']['hashtags'], 'username': tweet_data['user']['screen_name'],
                 'Created_date': created_date, 'Location': user_location, 'Tweet_text': tweet_text,
                 'Likes': user_likes, 'Timezone': tweet_data['user']['time_zone']}
        return tweet


def Prepare_df(tweet_cursor):
    df = pd.DataFrame(list(tweet_cursor))
    df_new = df.sort_values(by='Likes', ascending=False)
    df_new = df_new.reset_index(drop=True)
    return df, df_new


def print_top5_liked_tweets(df):
    if len(df) > 5:
        for j in range(5):
            print(df.iloc[j, 7], '--', df.iloc[j, 8])
            print('\n')


def saveplot(df):
    df['Created_date'] = pd.to_datetime(df['Created_date'])
    df_final = df.groupby(
        [pd.Grouper(key='Created_date', freq='H')]).size().reset_index(name='count')
    df_final.plot(x='Created_date', y='count', kind='line', c='r')
    plt.savefig('/home/ec2-user/BuffOverflow/static/tweet_countimg.png')


def hastagsplot(df):
    df['hashtag'] = df['Tweet_text'].apply(
        lambda x: re.findall(r'\B#\w*[a-zA-Z]+\w*', x))
    X = []
    for i in df['hashtag'].values:
        for k in i:
            X.append(k)
    d = Counter(X)
    # print(d)
    df = pd.DataFrame.from_dict(d, orient='index').reset_index()
    df = df.rename(columns={'index': 'Hashtags', 0: 'Count'})
    print(df.head())
    #plt.bar(df['Hashtags'].head(), df['Count'].head(), color='blue')
    # plt.xlabel("Hashtags")
    # plt.xticks(fontsize=10)
    #plt.ylabel("Hashtag Count in tweets")
    #plt.title("Top 5 hashtags")
    # plt.savefig('/home/ec2-user/buff-overflow/hashtagsimage.png')


def tweet_tokenizer(tweet_text):
    try:
        tokenizer = TweetTokenizer()
        all_tokens = tokenizer.tokenize(tweet_text.lower())
        # this line filters out all tokens that are entirely non-alphabetic characters
        filtered_tokens = [t for t in all_tokens if t.islower()]
        # filter out all tokens that are <=2 chars
        filtered_tokens = [x for x in filtered_tokens if len(x) > 2]
    except IndexError:
        filtered_tokens = []
    return(filtered_tokens)


def get_frequent_terms(text_series, stop_words=None, ngram_range=(1, 2)):
    count_vectorizer = CountVectorizer(analyzer="word",
                                       tokenizer=tweet_tokenizer,
                                       stop_words=stop_words, ngram_range=ngram_range)
    term_freq_matrix = count_vectorizer.fit_transform(text_series)
    terms = count_vectorizer.get_feature_names()
    term_frequencies = term_freq_matrix.sum(axis=0).tolist()[0]

    term_freq_df = (pd.DataFrame(list(zip(terms, term_frequencies)), columns=["token", "count"])
                    .set_index("token")
                    .sort_values("count", ascending=False))
    return term_freq_df


class StdOutListener(StreamListener):
    def on_data(self, data):
        tweet_data = json.loads(data)
        # print(tweet_data)
        try:
            tweet = Prepare_Tweet(tweet_data)
            if tweet is not None:
                print(tweet)
                colq.insert_one(tweet)
                tweet_cursor = colq.find()
                orig_df, sorted_df = Prepare_df(tweet_cursor)
                print_top5_liked_tweets(sorted_df)
                saveplot(orig_df)
                hastagsplot(orig_df)
                df_text_word = get_frequent_terms(
                    orig_df["Tweet_text"], stop_words="english")
                df_text_word.reset_index(level=0, inplace=True)
                data = dict(zip(df_text_word['token'].tolist(), df_text_word['count'].tolist()))
                print(data)
                wc = WordCloud(width=800, height=400,
                               max_words=100).generate_from_frequencies(data)
                plt.figure(figsize=(10, 10))
                plt.imshow(wc, interpolation='bilinear')
                plt.axis('off')
                wc.to_file("/home/ec2-user/buff-overflow/HW6/wcimg.png")
                print(df_text_word.head(7))
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
