from flask import Flask
from sys import version

app = Flask(__name__)

@app.route("/")
def index():
    return "API interface not yet implemented"

application = app
