from app import app
# basic test server. NOT SUITABLE FOR PRODUCTION.
# Use a wsgi wrapper like geven, gunicorn or tornado for deployement.

if __name__ == "__main__":
    app.debug = True  # lotta stuff on your stdout
    app.run(threaded=True, port=80, host='0.0.0.0')  # public reachable
