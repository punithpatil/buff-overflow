from flask import Flask, render_template
import re
from pymongo import MongoClient
from collections import Counter
from bson import json_util
import json
import pandas as pd
connection = MongoClient('localhost', 27017)
collection = connection.db.tweets_sfe

application = Flask(__name__)

@application.route("/user")
def user():
    return render_template('user.html')

@application.route("/")
def hello():
    # documents = collection.find()
    # response = []
    # for document in documents:
    # document['_id'] = str(document['_id'])
    # response.append(document)
    # print(json.dumps(response))
    # return render_template('sample.html',data=json.dumps(response))
    tweet_cursor = collection.find()
    df1 = pd.DataFrame(list(tweet_cursor))
    print("Df1 columns:",df1.columns)
    df = df1.sort_values(by='Likes', ascending=False)
    df = df.reset_index(drop=True)
    x = []
    Y = []
    p = []
    q = []
    x1=[]
    y1=[]
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

    df1['hashtag'] = df1['Tweet_text'].apply(lambda x: re.findall(r'\B#\w*[a-zA-Z]+\w*', x))
    temp = []
    for i in df1['hashtag'].values:
        for k in i:
            temp.append(k)

    d = Counter(temp)
    #print(d)
    df2 = pd.DataFrame.from_dict(d, orient='index').reset_index()
    df2.columns = ['Hashtags','tweet_c']
    print("Values:",df2['Hashtags'].values,"- type", type(df2['Hashtags']))
    print(df2['tweet_c'].values)
    x1.extend(df2['Hashtags'].tolist())
    y1.extend(df2['tweet_c'].tolist())
    print("X1 values:",x1[:5])
    print("Y1 values:",y1[:5])

    return render_template('dashboard.html',labels=x[-10:], values=Y[-10:],legend="Number of tweets",tweets=zip(p,q))

@application.route('/map')
def map():
    map_bool=True
    documents = collection.find()
    response = []
    for document in documents:
        document['_id'] = str(document['_id'])
        response.append(document)
    #print(json.dumps(response,default=json_util.default))
    return render_template('index2.html',data=json.dumps(response,default=json_util.default),map_bool=map_bool)


if __name__ == "__main__":
    application.debug = True
    application.run(host='0.0.0.0', port=5000)
