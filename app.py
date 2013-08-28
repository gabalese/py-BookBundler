from flask import Flask, request
app = Flask(__name__)
app.debug = True


@app.route("/", methods=["GET", "POST"])
def hello():
    if request.method == "POST":
        return "POSTED!"
    return "Hello World!"
