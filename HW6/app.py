from flask import Flask, render_template
hello_app = Flask(__name__)

@hello_app.route("/")
def hello():
    return render_template('index.html')

if __name__ == "__main__": 
    hello_app.run(host="0.0.0.0", port="5000")
