from flask import Flask
hello_app = Flask(__name__)

@hello_app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__": 
    hello_app.run(host="0.0.0.0", port="5000")