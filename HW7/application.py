from flask import Flask, render_template
from pymongo import MongoClient
import json
import pandas as pd
connection = MongoClient('localhost', 27017)
collection = connection.db.tweets_sfe

application = Flask(__name__)

@application.route("/user")
def user():
    return render_template('user.html')

@application.route("/dashboard")
def dashboard():
    return  render_template('dashboard.html')

@application.route("/")
def hello():
    tweet_cursor = collection.find()
    df = pd.DataFrame(list(tweet_cursor))
    df = df.sort_values(by='Likes', ascending=False)
    df = df.reset_index(drop=True)
    x = []
    Y = []
    p = []
    q = []
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
    return render_template('dashboard.html',labels=x, values=Y,legend="Number of tweets",tweets=zip(p,q))


if __name__ == "__main__":
    application.debug = True
    application.run(host='0.0.0.0', port=5000)
