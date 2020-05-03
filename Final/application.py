from flask import Flask, render_template
import re
import os
import time
from pymongo import MongoClient
from collections import Counter
from bson import json_util
import json
import pandas as pd
connection = MongoClient('localhost', 27017)
collection = connection.db.tweets_sfe
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.tokenize import TweetTokenizer
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer

#Flask Application Instance
application = Flask(__name__)

#Tweet Tokenizing and Filtering Method
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


#Method to get frequent tweets
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

#Route to Team Page
@application.route("/user")
def user():
    return render_template('user.html')

#Route to Home Page
@application.route("/")
def hello():
    tweet_cursor = collection.find()
    df1 = pd.DataFrame(list(tweet_cursor))
    df = df1.sort_values(by='Likes', ascending=False)
    df = df.reset_index(drop=True)
    x = []
    Y = []
    p = []
    q = []
    x1=[]
    y1=[]
    
    #Sending Tweet Frequency To Templates
    if len(df) > 5:
        for j in range(5):
            p.append(df.iloc[j, 7])
            q.append(df.iloc[j, 8])
        df['Created_date'] = pd.to_datetime(df['Created_date'])
        df_final = df.groupby([pd.Grouper(key='Created_date', freq='H')]).size().reset_index(name='count')
        df_list = df_final.values.tolist()
        for key, value in df_list:
            x.append(key)
            Y.append(value)
            
    #Sending Hashtag Frequency To Templates
    df1['hashtag'] = df1['Tweet_text'].apply(lambda x: re.findall(r'\B#\w*[a-zA-Z]+\w*', x))
    temp = []
    for i in df1['hashtag'].values:
        for k in i:
            temp.append(k)
    d = Counter(temp)
    df2 = pd.DataFrame.from_dict(d, orient='index').reset_index()
    df2.columns = ['Hashtags','tweet_c']
    x1.extend(df2['Hashtags'].tolist())
    y1.extend(df2['tweet_c'].tolist())
   
    #Sending Word Cloud Data To Templates
    df_text_word = get_frequent_terms(df1["Tweet_text"], stop_words="english")
    df_text_word.reset_index(level=0, inplace=True)
    data = dict(zip(df_text_word['token'].tolist(), df_text_word['count'].tolist()))
    print(data)
    wc = WordCloud(width=800, height=400,max_words=100).generate_from_frequencies(data)
    plt.figure(figsize=(10, 10))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    chart_name="chart"+str(time.time())+".png"
    for filename in os.listdir('static/images/'):
        if filename.startswith('chart'):  # not to remove other images
            print("hi")
            print(filename)
            os.remove('static/images/' + filename)
    wc.to_file("/home/ec2-user/BuffOverflow/static/images/"+chart_name)
    return render_template('dashboard.html',labels=x[-10:], values=Y[-10:],legend="Number of tweets",tweets=zip(p,q),x1=x1[:5],y1=y1[:5],chart_name=chart_name)

#Route to Maps Page
@application.route('/map')
def map():
    map_bool=True
    documents = collection.find()
    response = []
    for document in documents:
        document['_id'] = str(document['_id'])
        response.append(document)
    return render_template('map.html',data=json.dumps(response,default=json_util.default),map_bool=map_bool)

if __name__ == "__main__":
    application.debug = True
    application.run(host='0.0.0.0', port=5000)
